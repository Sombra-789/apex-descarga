import importlib.util
import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('package_windows', ROOT / 'scripts/package_windows.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class PackageTests(unittest.TestCase):
    def test_package_excludes_runtime_data_and_rejects_mixed_versions(self):
        with TemporaryDirectory() as temp:
            source = Path(temp) / 'source'
            shutil.copytree(ROOT / 'brave-windows', source)
            (source / 'windows/settings.json').write_text('{"download_folder":"private"}')
            (source / 'extension/cookies.txt').write_text('private')
            with patch.object(mod, 'SOURCE', source):
                target = mod.package(Path(temp) / 'out')
                with zipfile.ZipFile(target) as archive:
                    names = archive.namelist()
                    self.assertTrue(any(n.endswith('/extension/site-policy.js') for n in names))
                    self.assertFalse(any('settings.json' in n or 'cookies.txt' in n or '__pycache__' in n for n in names))
                manifest = source / 'extension/manifest.json'
                data = json.loads(manifest.read_text(encoding='utf-8'))
                data['version'] = '1.0.0'
                manifest.write_text(json.dumps(data), encoding='utf-8')
                with self.assertRaisesRegex(ValueError, 'versiones'):
                    mod.package(Path(temp) / 'bad-output')
                self.assertFalse((Path(temp) / 'bad-output').exists())
