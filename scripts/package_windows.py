"""Build a clean Windows ZIP and reject mixed component versions."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'brave-windows'


def package(output):
    manifest = json.loads((SOURCE / 'extension/manifest.json').read_text(encoding='utf-8'))
    version = manifest['version']
    tree = ast.parse((SOURCE / 'windows/host.py').read_text(encoding='utf-8'))
    host_version = next(ast.literal_eval(node.value) for node in tree.body
                        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'VERSION' for t in node.targets))
    if version != host_version or manifest['action']['default_title'] != f'Apex Descarga {version}':
        raise ValueError('Las versiones del paquete no coinciden')
    files = [p for p in SOURCE.rglob('*') if p.is_file() and (
        (p.parent == SOURCE and p.suffix in ('.md', '.cmd')) or
        (p.parent == SOURCE / 'windows' and p.suffix in ('.py', '.ps1', '.cs')) or
        (p.parent == SOURCE / 'extension' and p.suffix in ('.js', '.html', '.css', '.json')) or
        (p.parent == SOURCE / 'extension/icons' and p.suffix == '.png'))]
    required = ['extension/site-policy.js', 'windows/validate-package.ps1', 'windows/install-first.ps1',
                'windows/upgrade.ps1', 'windows/launcher.cs', 'ACTUALIZAR_APEX.cmd', 'INSTALAR_POR_PRIMERA_VEZ.cmd']
    for name in required:
        if SOURCE / name not in files:
            raise ValueError(f'Paquete incompleto: {name}')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    name = f'Apex-Descarga-Windows-{version}'
    target = output / f'{name}.zip'
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(files):
            archive.write(file, f'{name}/{file.relative_to(SOURCE).as_posix()}')
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    (output / f'{name}.zip.sha256').write_text(f'{digest}  {target.name}\n', encoding='ascii')
    return target


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    print(package(parser.parse_args().output))
