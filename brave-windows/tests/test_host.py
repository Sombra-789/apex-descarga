import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import time
from tempfile import TemporaryDirectory
import threading
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
HOST = ROOT / 'windows' / 'host.py'
spec = importlib.util.spec_from_file_location('apex_host_12', HOST)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class URLTests(unittest.TestCase):
    def test_public_urls(self):
        for u in ('https://youtu.be/123', 'https://vimeo.com/123', 'http://example.com/a'):
            with self.subTest(u=u): self.assertEqual(mod.validate_url(u), u)
    def test_invalid_urls(self):
        for u in ('file:///etc/passwd', 'javascript:alert(1)', 'ftp://site.com/',
                  'https://127.0.0.1/', 'http://10.1.0.1/', 'http://[::1]/',
                  'https://localhost/a', 'http://foo.local', 'https://a:secret@example.com',
                  'https://example.com:8999/', 'https://example.com/a\nb', '', 'x' * 2001,
                  'https://user@example.com', 'http://192.168.0.1'):
            with self.subTest(u=u), self.assertRaises(ValueError): mod.validate_url(u)
    def test_invalid_types(self):
        for u in (None, {}, [], 42):
            with self.subTest(u=u), self.assertRaises(ValueError): mod.validate_url(u)


class FolderTests(unittest.TestCase):
    def test_default_folder_without_settings(self):
        with TemporaryDirectory() as temp, patch.object(mod, 'CONFIG_FILE', Path(temp) / 'missing.json'):
            self.assertEqual(mod.folder(), mod.default_folder())

    def test_custom_folder_persisted(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / 'Mis descargas' / 'Videos'
            target.mkdir(parents=True)
            with patch.object(mod, 'CONFIG_FILE', root / 'settings.json'):
                self.assertEqual(mod.save_folder(target), target)
                self.assertEqual(mod.folder(), target)
                self.assertEqual(mod.load_settings()['download_folder'], str(target))
                self.assertIn(str(target), mod.build_args('https://example.com/a','mp4','1080','stable',True))
                with patch.object(mod.os, 'startfile', create=True) as opener, patch.object(mod.sys, 'platform', 'win32'):
                    self.assertTrue(mod.open_folder()['ok'])
                    opener.assert_called_once_with(str(target))

    def test_invalid_folder_not_saved(self):
        with TemporaryDirectory() as temp, patch.object(mod, 'CONFIG_FILE', Path(temp) / 'settings.json'):
            with self.assertRaises(ValueError):
                mod.save_folder(Path(temp) / 'no existe')
            self.assertEqual(mod.folder(), mod.default_folder())

    def test_corrupt_settings_falls_back(self):
        with TemporaryDirectory() as temp:
            config = Path(temp) / 'settings.json'
            config.write_text('not json', encoding='utf-8')
            with patch.object(mod,'CONFIG_FILE',config):
                self.assertEqual(mod.folder(), mod.default_folder())

    def test_choose_folder_success(self):
        with TemporaryDirectory() as temp:
            target = Path(temp) / 'público'
            target.mkdir()
            result = subprocess.CompletedProcess([],0,('APEX_FOLDER:' + str(target) + '\n').encode('utf-8'),b'')
            with patch.object(mod.sys,'platform','win32'), patch.object(mod,'CONFIG_FILE',Path(temp)/'settings.json'), \
                 patch.object(mod.subprocess,'run',return_value=result) as run:
                response = mod.choose_folder()
                self.assertEqual(response['folder'],str(target))
                self.assertFalse(response['cancelled'])
                self.assertTrue(run.call_args.kwargs['shell'] is False)
                self.assertEqual(run.call_args.kwargs['timeout'],300)
                self.assertIn('-EncodedCommand',run.call_args.args[0])

    def test_choose_folder_cancel_keeps_existing(self):
        with TemporaryDirectory() as temp:
            target=Path(temp) / 'Mi música';target.mkdir()
            result=subprocess.CompletedProcess([],0,b'APEX_CANCELLED\n',b'')
            with patch.object(mod.sys,'platform','win32'), patch.object(mod,'CONFIG_FILE',Path(temp)/'settings.json'), \
                 patch.object(mod.subprocess,'run',return_value=result):
                mod.save_folder(target)
                response=mod.choose_folder()
                self.assertTrue(response['cancelled'])
                self.assertEqual(response['folder'],str(target))
                self.assertEqual(mod.folder(),target)

    def test_choose_folder_error_no_change(self):
        with TemporaryDirectory() as temp:
            result = subprocess.CompletedProcess([],1,b'',b'error')
            with patch.object(mod.sys,'platform','win32'), patch.object(mod,'CONFIG_FILE',Path(temp)/'settings.json'), \
                 patch.object(mod.subprocess,'run',return_value=result):
                with self.assertRaises(ValueError): mod.choose_folder()
                self.assertEqual(mod.folder(),mod.default_folder())


class FormatTests(unittest.TestCase):
    def test_selector_mp4(self):
        self.assertIn('bv[height<=1080][vcodec^=avc1]+ba[acodec^=mp4a]', mod.format_selector('1080','stable'))
    def test_selector_hls(self):
        self.assertIn('[protocol*=m3u8]', mod.format_selector('720','compatible'))
    def test_unlimited(self):
        self.assertNotIn('height<=', mod.format_selector('best','stable'))
    def test_command_secure(self):
        args = mod.build_args('https://example.org/a', 'mp4','1080','stable', True)
        self.assertEqual(args[:3],[sys.executable,'-m','yt_dlp'])
        self.assertIn('--ignore-config',args)
        self.assertIn('--merge-output-format',args)
        self.assertIn('--no-playlist',args)
        self.assertEqual(args[-1],'https://example.org/a')
    def test_audio(self):
        args = mod.build_args('https://example.org/a','mp3','best','stable',True)
        self.assertIn('--extract-audio',args)
        self.assertIn('--audio-format',args)
    def test_without_ffmpeg(self):
        args = mod.build_args('https://example.org/a','mp4','720','stable',False)
        self.assertNotIn('--merge-output-format',args)

class PreviewTests(unittest.TestCase):
    def test_simplify(self):
        payload={'title':'Canción','channel':'Ejemplo','duration':84.7,'extractor_key':'Youtube',
                 'thumbnail':'https://example.com/p.jpg', 'formats':[
                     {'height':720, 'vcodec':'avc1.4'}, {'height':1080, 'vcodec':'av01'},
                     {'height':None,'vcodec':'none'}, {'height':720,'vcodec':'avc1'}]}
        result=mod.simplify_metadata(payload)
        self.assertEqual(result['heights'],[720,1080])
        self.assertEqual(result['duration'],84)
        self.assertEqual(result['title'],'Canción')
    def test_no_playlist(self):
        with self.assertRaisesRegex(ValueError,'video'):
            mod.simplify_metadata({'_type':'playlist'})
    def test_thumbnail_HTTPS(self):
        self.assertEqual(mod.safe_thumbnail({'thumbnail':'http://example.com/image.png'}),'')
    def test_preview_uses_executable_without_shell(self):
        fake = subprocess.CompletedProcess(args=[], returncode=0, stdout=b'{"title":"Video","formats":[]}',stderr=b'')
        with patch.object(mod,'ytdlp_version',return_value='test'), patch.object(mod.subprocess,'run',return_value=fake) as proc:
            data=mod.preview('https://example.com/v')
            self.assertEqual(data['title'],'Video')
            self.assertFalse(proc.call_args.kwargs['shell'])
            self.assertEqual(proc.call_args.kwargs['timeout'],35)
    def test_preview_timeout(self):
        with patch.object(mod,'ytdlp_version',return_value='test'), patch.object(mod.subprocess,'run',side_effect=subprocess.TimeoutExpired('yt-dlp',35)):
            with self.assertRaisesRegex(ValueError,'35 segundos'): mod.preview('https://example.com/v')
    def test_preview_invalid_output(self):
        fake = subprocess.CompletedProcess([],0,b'not json',b'')
        with patch.object(mod,'ytdlp_version',return_value='test'), patch.object(mod.subprocess,'run',return_value=fake):
            with self.assertRaises(ValueError): mod.preview('https://example.com/v')

class ProtocolTests(unittest.TestCase):
    def exchange(self, message):
        raw = json.dumps(message).encode('utf-8')
        result = subprocess.run([sys.executable,str(HOST)],input=struct.pack('<I',len(raw))+raw,
                                capture_output=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr.decode())
        size=struct.unpack('<I',result.stdout[:4])[0]
        self.assertEqual(len(result.stdout),size+4)
        return json.loads(result.stdout[4:])
    def test_status(self):
        result=self.exchange({'type':'status'})
        self.assertEqual(result['version'],'1.2.3')
        self.assertEqual(result['type'],'status')
    def test_unknown_command(self):
        self.assertEqual(self.exchange({'type':'wat'})['type'],'error')
    def test_reject_local_preview(self):
        self.assertEqual(self.exchange({'type':'preview','url':'http://localhost'})['type'],'error')
    def test_oversized_input(self):
        process=subprocess.run([sys.executable,str(HOST)],input=struct.pack('<I',mod.MAX_MESSAGE+1),capture_output=True,timeout=10)
        size=struct.unpack('<I',process.stdout[:4])[0]
        self.assertEqual(json.loads(process.stdout[4:4+size])['type'],'error')

class DownloadTests(unittest.TestCase):
    def settings(self):
        return {'url':'https://example.com/v', 'format':'mp4','quality':'1080','mode':'stable'}
    def mocks(self):
        return None
    def test_mp3_needs_ffmpeg(self):
        with patch.object(mod,'ytdlp_version',return_value='ok'), patch.object(mod.shutil,'which',return_value=None):
            with self.assertRaisesRegex(ValueError,'FFmpeg'):
                mod.download({**self.settings(),'format':'mp3'},listen_for_cancel=False)
    def test_success(self):
        with TemporaryDirectory() as temp, patch.object(mod,'folder',return_value=Path(temp)), \
          patch.object(mod,'ytdlp_version',return_value='ok'), patch.object(mod.shutil,'which',return_value='ffmpeg'), \
          patch.object(mod,'run_ytdlp',return_value=(0,'','C:/Downloads/video.mp4',False)), patch.object(mod,'send') as send:
            mod.download(self.settings(), listen_for_cancel=False)
            self.assertEqual(send.call_args.args[0]['file'],'video.mp4')
            self.assertTrue(send.call_args.args[0]['ok'])
    def test_retry_on_403(self):
        with TemporaryDirectory() as temp, patch.object(mod,'folder',return_value=Path(temp)), \
          patch.object(mod,'ytdlp_version',return_value='ok'), patch.object(mod.shutil,'which',return_value='ffmpeg'), \
          patch.object(mod,'run_ytdlp',side_effect=[(1,'HTTP Error 403: Forbidden','',False),(0,'','C:/data/test.mp4',False)]) as runner, \
          patch.object(mod,'send') as send:
            mod.download(self.settings(),listen_for_cancel=False)
            self.assertEqual(runner.call_count,2)
            self.assertTrue(send.call_args.args[0]['ok'])
    def test_no_retry_on_other(self):
        with TemporaryDirectory() as temp, patch.object(mod,'folder',return_value=Path(temp)), \
          patch.object(mod,'ytdlp_version',return_value='ok'), patch.object(mod.shutil,'which',return_value='ffmpeg'), \
          patch.object(mod,'run_ytdlp',return_value=(1,'Unsupported URL','',False)) as runner, \
          patch.object(mod,'send') as send:
            mod.download(self.settings(),listen_for_cancel=False)
            self.assertEqual(runner.call_count,1)
            self.assertFalse(send.call_args.args[0]['ok'])
    def test_real_subprocess_cancel_watchdog(self):
        event=threading.Event()
        script='import sys,time;print("[download] 12.0% of 5MiB",flush=True);time.sleep(20)'
        def trigger():
            time.sleep(0.4)
            event.set()
        t=threading.Thread(target=trigger,daemon=True)
        t.start()
        begin=time.monotonic()
        with patch.object(mod,'send') as send:
            code, error, output, cancelled = mod.run_ytdlp(
                [sys.executable,'-u','-c',script],1,1,event)
        self.assertTrue(cancelled)
        self.assertLess(time.monotonic()-begin,5)
        self.assertNotEqual(code,0)
        self.assertGreater(send.call_count,0)

    def test_cancelled(self):
        with TemporaryDirectory() as temp, patch.object(mod,'folder',return_value=Path(temp)), \
          patch.object(mod,'ytdlp_version',return_value='ok'), patch.object(mod.shutil,'which',return_value='ffmpeg'), \
          patch.object(mod,'run_ytdlp',return_value=(1,'','',True)), patch.object(mod,'send') as send:
            mod.download(self.settings(),listen_for_cancel=False)
            self.assertTrue(send.call_args.args[0]['cancelled'])
    def test_friendly_error(self):
        self.assertIn('403',mod.friendly_error('HTTP Error 403: Forbidden'))
        self.assertIn('enlace',mod.friendly_error('Unsupported URL'))

if __name__=='__main__':unittest.main()
