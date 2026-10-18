"""Tests of Smart Merge's offline security controls and local transaction workflow."""
import contextlib
import io
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

FILE = Path(__file__).resolve().parents[1] / 'windows' / 'smart_merge.py'
spec = importlib.util.spec_from_file_location('smart_merge_test', FILE)
sm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sm)

def public_url(num, group='archive', pad=2):
    return f'https://www.mediafire.com/file/id{num}/{group}.part{num:0{pad}d}.rar/file'

class FakeResponse(io.BytesIO):
    status = 200
    def __init__(self, url, content, headers=None):
        super().__init__(content)
        self._url = url
        self.headers = headers or {'Content-Length': str(len(content)), 'Content-Type': 'application/octet-stream'}
    def geturl(self):
        return self._url

class Analysis(unittest.TestCase):
    def test_orders_numbers(self):
        result = sm.analyze([public_url(3), public_url(1), public_url(2)])
        self.assertEqual([p['number'] for p in result['parts']], [1, 2, 3])
        self.assertEqual(result['base'], 'archive')

    def test_missing_parts(self):
        with self.assertRaisesRegex(sm.MergeError, 'Faltan partes'):
            sm.analyze([public_url(1), public_url(3)])

    def test_duplicates(self):
        with self.assertRaisesRegex(sm.MergeError, 'repetidas'):
            sm.analyze([public_url(1), public_url(1)])

    def test_mixed_groups(self):
        with self.assertRaisesRegex(sm.MergeError, 'mismo archivo'):
            sm.analyze([public_url(1), public_url(2, group='other')])

    def test_mixed_padding_rejected(self):
        with self.assertRaisesRegex(sm.MergeError, 'uniforme'):
            sm.analyze([public_url(1, pad=1), public_url(2, pad=2)])

    def test_security_blocks_local_hosts_and_non_mediafire(self):
        for url in ('file:///a', 'http://www.mediafire.com/a',
                    'https://www.mediafire.com.evil.com/a',
                    'https://localhost/a', 'https://127.0.0.1/a',
                    'https://user:secret@www.mediafire.com/a',
                    'https://www.mediafire.com:9090/a', 'https://example.com/a'):
            with self.subTest(url=url), self.assertRaises(sm.MergeError):
                sm.check_url(url)

    def test_min_max(self):
        with self.assertRaisesRegex(sm.MergeError, 'entre 2 y 100'):
            sm.analyze([public_url(1)])

class Download(unittest.TestCase):
    def test_download_stream_and_cached_sha256(self):
        payload = b'Rar!\x1a\x07\x01' + b'\0' * 999
        data = [public_url(1), public_url(2)]
        manifest = sm.analyze(data)
        opened = []
        def serve(url, headers=None, timeout=35):
            opened.append(headers or {})
            return FakeResponse(url, payload)
        with tempfile.TemporaryDirectory() as temp, patch.object(sm, '_open', serve):
            work = Path(temp)
            tracker = sm.Progress(2, lambda m: None)
            one = sm._download_one(manifest['parts'][0], work, threading.Event(), tracker)
            self.assertEqual(one.read_bytes(), payload)
            self.assertEqual(one.name, 'archive.part01.rar')
            self.assertTrue((work / 'archive.part01.rar.verified.json').is_file())
            two = sm._download_one(manifest['parts'][0], work, threading.Event(), tracker)
            self.assertEqual(one, two)
            self.assertEqual(len(opened), 1)

    def test_rejects_html_download(self):
        url = public_url(1)
        def serve(link, headers=None, timeout=35):
            if '/file/' in link:
                return FakeResponse(link, b'<html>no link</html>', {'Content-Type': 'text/html'})
            raise AssertionError('Unexpected direct download')
        with tempfile.TemporaryDirectory() as temp, patch.object(sm, '_open', serve):
            with self.assertRaisesRegex(sm.MergeError, 'Parte 01'):
                sm._download_one(sm.analyze([url, public_url(2)])['parts'][0],
                                 Path(temp), threading.Event(), sm.Progress(2, lambda m:None))

class Archive(unittest.TestCase):
    def test_rejects_traversal(self):
        for name in ('../escape', 'C:\\Users\\bad.txt', 'CON.txt'):
            sample = 'Path = archive.rar\r\nType = Rar\r\n\r\n----------\r\nPath = ' + name + '\r\nFolder = -\r\nSize = 1\r\n\r\n'
            with self.subTest(name=name), self.assertRaises(sm.MergeError):
                sm._validate_members(sample)

    def test_reports_sizes(self):
        sample = 'Path = archive.rar\r\nType = Rar\r\n\r\n----------\r\nPath = file.txt\r\nFolder = -\r\nSize = 5\r\n\r\n'
        self.assertEqual(sm._validate_members(sample), (1, 5))

    def test_end_to_end_orchestration_with_fake_parts_and_7zip(self):
        urls = [public_url(1), public_url(2)]
        events = []
        def fake_download(part, work, cancel, progress):
            out = work / part['name']
            out.write_bytes(b'Rar!\x1a\x07\x01abcdefgh')
            progress.update(part['number'], out.stat().st_size, out.stat().st_size, done=True)
            return out
        def fake_7zip(command, cancel, **kw):
            action = command[1]
            if action == 'l':
                return 'Path = archive.rar\r\nType = Rar\r\n\r\n----------\r\nPath = contenido.txt\r\nFolder = -\r\nSize = 3\r\n\r\n'
            if action == 'x':
                extracted = Path(next(x[2:] for x in command if x.startswith('-o')))
                (extracted / 'contenido.txt').write_text('hey')
            if action == 'a':
                Path(command[-2]).write_bytes(b'fake-final-package')
            return ''
        with tempfile.TemporaryDirectory() as temp, \
             patch.object(sm, 'find_7zip', return_value='7z'), \
             patch.object(sm, '_download_one', side_effect=fake_download), \
             patch.object(sm, '_process', side_effect=fake_7zip):
            result = sm.execute({'urls':urls, 'parallel':2, 'output':'zip', 'cleanup':True},
                                events.append, threading.Event(), Path(temp))
            self.assertTrue(result['ok'])
            self.assertEqual(result['file'], 'archive-' + hashlib_of(urls) + '.zip')
            self.assertTrue(Path(result['path']).exists())
            self.assertTrue(result['sha256'])
            work = Path(temp) / 'SmartMerge_Work'
            self.assertEqual(list(work.iterdir()), [])
            self.assertTrue(any(event.get('stage') == 'verify_output' for event in events))

    def test_output_setting_validation(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(sm, 'find_7zip', return_value='7z'):
            with self.assertRaisesRegex(sm.MergeError, 'Formato'):
                sm.execute({'urls': [public_url(1), public_url(2)], 'parallel':2,
                            'output':'exe', 'cleanup':True}, lambda x:None, threading.Event(), Path(temp))

def hashlib_of(urls):
    import hashlib
    return hashlib.sha256('\n'.join(urls).encode()).hexdigest()[:20]

if __name__ == '__main__':
    unittest.main()
