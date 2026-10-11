#!/usr/bin/env python3
"""Apex Descarga 1.2.2 Native Messaging host.
Only explicit user-submitted HTTP(S) URLs. Runs yt-dlp without a shell,
never imports browser cookies, and only writes downloaded media to the user-selected folder.
Native Messaging wire protocol: little-endian uint32 + JSON UTF-8.
"""
from __future__ import annotations

import importlib.metadata
import base64
import ipaddress
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import threading
import time
from urllib.parse import urlsplit

VERSION = '1.2.2'
MAX_MESSAGE = 1024 * 1024
MAX_PREVIEW = 4 * 1024 * 1024
PERCENT = re.compile(r'(?<!\d)(\d{1,3}(?:\.\d+)?)%')
ANSI = re.compile(r'\x1b\[[0-9;]*[A-Za-z]')
ALLOWED_QUALITY = {'best', '480', '720', '1080', '2160'}
ALLOWED_MODE = {'stable', 'compatible'}


def send(payload):
    payload_bytes = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    if len(payload_bytes) > MAX_MESSAGE:
        raise ValueError('Respuesta demasiado grande.')
    sys.stdout.buffer.write(struct.pack('<I', len(payload_bytes)) + payload_bytes)
    sys.stdout.buffer.flush()


def recv():
    header = sys.stdin.buffer.read(4)
    if not header:
        return None
    if len(header) != 4:
        raise ValueError('Cabecera incompleta.')
    length = struct.unpack('<I', header)[0]
    if not 2 <= length <= MAX_MESSAGE:
        raise ValueError('Longitud del mensaje inválida.')
    data = bytearray()
    while len(data) < length:
        chunk = sys.stdin.buffer.read(length - len(data))
        if not chunk:
            raise EOFError('Mensaje incompleto.')
        data.extend(chunk)
    parsed = json.loads(data)
    if not isinstance(parsed, dict):
        raise ValueError('Se esperaba un objeto JSON.')
    return parsed


def validate_url(raw):
    if not isinstance(raw, str) or not 1 <= len(raw.strip()) <= 2000:
        raise ValueError('Introduce un enlace HTTP(S) de hasta 2000 caracteres.')
    value = raw.strip()
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        raise ValueError('El enlace contiene caracteres no permitidos.')
    try:
        parsed = urlsplit(value)
        if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError('Solo se aceptan enlaces HTTP o HTTPS sin credenciales.')
        hostname = parsed.hostname.lower().rstrip('.')
        if (hostname in ('localhost', 'localhost.localdomain') or
                hostname.endswith(('.localhost', '.local', '.internal', '.test', '.invalid'))):
            raise ValueError('No se admiten direcciones locales.')
        try:
            ip = ipaddress.ip_address(hostname)
        except ValueError:
            pass
        else:
            if not ip.is_global:
                raise ValueError('No se admiten IP privadas o reservadas.')
        if parsed.port is not None and parsed.port not in (80, 443):
            raise ValueError('Solo se aceptan puertos web estándar.')
    except ValueError as error:
        raise ValueError(str(error) or 'Enlace inválido.') from error
    return value


CONFIG_FILE = Path(__file__).resolve().parent / 'settings.json'


def default_folder():
    return Path.home() / 'Downloads' / 'Apex Descarga'


def load_settings():
    try:
        settings = json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
        if not isinstance(settings, dict):
            return {}
        return settings
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}


def folder():
    selected = load_settings().get('download_folder')
    if isinstance(selected, str) and selected and len(selected) <= 1024 and Path(selected).is_absolute():
        return Path(selected)
    return default_folder()


def save_folder(directory):
    directory = Path(directory)
    if not directory.is_absolute() or not directory.is_dir():
        raise ValueError('La carpeta seleccionada no existe o no es válida.')
    if len(str(directory)) > 1024:
        raise ValueError('La ruta de la carpeta es demasiado larga.')
    settings = load_settings()
    settings['download_folder'] = str(directory)
    temp_path = CONFIG_FILE.with_name('settings.json.tmp')
    try:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        temp_path.write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding='utf-8')
        os.replace(temp_path, CONFIG_FILE)
    finally:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass
    return directory


# A fixed PowerShell script: no user text is ever interpolated into commands.
# The folder is selected directly by the human via a Windows Forms dialog.
WINDOWS_FOLDER_DIALOG = r"""
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$dialog = New-Object System.Windows.Forms.FolderBrowserDialog
$dialog.Description = 'Apex Descarga: selecciona la carpeta de destino'
$dialog.ShowNewFolderButton = $true
if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
    [Console]::WriteLine('APEX_FOLDER:' + $dialog.SelectedPath)
} else {
    [Console]::WriteLine('APEX_CANCELLED')
}
$dialog.Dispose()
"""


def choose_folder():
    if sys.platform != 'win32':
        raise ValueError('El selector de carpetas solo está disponible en Windows.')
    script = base64.b64encode(WINDOWS_FOLDER_DIALOG.encode('utf-16le')).decode('ascii')
    command = ['powershell.exe', '-NoProfile', '-STA', '-ExecutionPolicy', 'Bypass',
               '-EncodedCommand', script]
    try:
        completed = subprocess.run(command, stdin=subprocess.DEVNULL, capture_output=True, timeout=300, shell=False,
                                   creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    except subprocess.TimeoutExpired as error:
        raise ValueError('El selector de carpetas tardó demasiado. Inténtalo de nuevo.') from error
    if completed.returncode != 0:
        raise ValueError('Windows no pudo abrir el selector de carpetas. Revisa PowerShell.')
    output = completed.stdout.decode('utf-8-sig', errors='replace').strip().splitlines()
    match = next((line for line in output if line.startswith('APEX_FOLDER:')), None)
    if match is not None:
        selected = match[len('APEX_FOLDER:'):].strip()
        if not selected:
            raise ValueError('Windows devolvió una ruta vacía.')
        target = save_folder(selected)
        return {'type': 'choose_folder', 'ok': True, 'cancelled': False, 'folder': str(target)}
    if 'APEX_CANCELLED' in output:
        return {'type': 'choose_folder', 'ok': True, 'cancelled': True, 'folder': str(folder())}
    raise ValueError('Windows no devolvió ninguna carpeta. Inténtalo de nuevo.')


def ytdlp_version():
    try:
        return importlib.metadata.version('yt-dlp')
    except importlib.metadata.PackageNotFoundError:
        return None


def status():
    return {'type': 'status', 'ok': True, 'version': VERSION,
            'ytdlp': ytdlp_version(), 'ffmpeg': bool(shutil.which('ffmpeg')),
            'deno': bool(shutil.which('deno')), 'folder': str(folder())}


def format_selector(quality, mode):
    limit = '' if quality == 'best' else f'[height<={quality}]'
    if mode == 'stable':
        return (f'bv{limit}[vcodec^=avc1]+ba[acodec^=mp4a]/'
                f'bv{limit}[ext=mp4]+ba[ext=m4a]/'
                f'bv{limit}+ba/b{limit}')
    return (f'bv{limit}[protocol*=m3u8]+ba[protocol*=m3u8]/'
            f'bv{limit}+ba/b{limit}')


def build_args(url, media_format, quality, mode, has_ffmpeg):
    args = [sys.executable, '-m', 'yt_dlp', '--ignore-config', '--no-playlist',
            '--no-overwrites', '--windows-filenames', '--newline', '--no-colors',
            '--no-warnings', '--socket-timeout', '20', '--retries', '2',
            '--fragment-retries', '2', '--paths', str(folder()),
            '--output', '%(title).160B [%(id)s].%(ext)s',
            '--print', 'after_move:APEX_OUTPUT:%(filepath)s']
    if media_format == 'mp3':
        args += ['-f', 'bestaudio/best', '--extract-audio', '--audio-format', 'mp3',
                 '--audio-quality', '0']
    elif has_ffmpeg:
        args += ['-f', format_selector(quality, mode), '--merge-output-format', 'mp4']
    else:
        limit = '' if quality == 'best' else f'[height<={quality}]'
        args += ['-f', f'b{limit}[ext=mp4]/b{limit}/best']
    args.append(url)
    return args


def friendly_error(raw):
    error = str(raw or '').strip()
    low = error.lower()
    if 'http error 403' in low or '403 forbidden' in low:
        return 'El servidor rechazó el video (HTTP 403). Prueba la compatibilidad HLS u otro formato.'
    if 'unsupported url' in low:
        return 'El sitio no admite ese enlace. Usa la URL de un video concreto y no la página principal.'
    if 'requested format is not available' in low:
        return 'La calidad solicitada no existe en ese video. Prueba «Mejor disponible».'
    if 'sign in' in low or 'login required' in low or 'private video' in low:
        return 'Este contenido requiere acceso autorizado. Apex no obtiene cookies ni inicia sesión.'
    if 'video unavailable' in low:
        return 'El video no está disponible desde este enlace.'
    if 'timed out' in low or 'timeout' in low:
        return 'La conexión tardó demasiado. Revisa Internet e inténtalo de nuevo.'
    return error[:360] or 'No se pudo completar la descarga.'


def safe_thumbnail(info):
    value = info.get('thumbnail')
    if isinstance(value, str) and len(value) <= 2000 and value.startswith('https://'):
        return value
    return ''


def simplify_metadata(info):
    if not isinstance(info, dict):
        raise ValueError('El sitio devolvió metadatos inesperados.')
    if info.get('_type') in ('playlist', 'multi_video'):
        raise ValueError('Introduce un enlace a un solo video, no una lista o canal.')
    heights = set()
    for item in info.get('formats') or []:
        if not isinstance(item, dict) or item.get('vcodec') in (None, 'none'):
            continue
        height = item.get('height')
        if isinstance(height, int) and 80 <= height <= 4320:
            heights.add(height)
    duration = info.get('duration')
    title = str(info.get('title') or 'Contenido multimedia')[:160]
    channel = str(info.get('uploader') or info.get('channel') or '')[:100]
    return {'type': 'preview', 'ok': True, 'title': title, 'channel': channel,
            'duration': int(duration) if isinstance(duration, (float, int)) and 0 <= duration < 100000000 else None,
            'thumbnail': safe_thumbnail(info), 'heights': sorted(heights),
            'site': str(info.get('extractor_key') or info.get('extractor') or '')[:50]}


def preview(url):
    if not ytdlp_version():
        raise ValueError('Falta yt-dlp en el Python configurado.')
    arguments = [sys.executable, '-m', 'yt_dlp', '--ignore-config', '--no-playlist',
                 '--skip-download', '--dump-single-json', '--no-warnings', '--no-colors',
                 '--socket-timeout', '10', '--retries', '1', '--extractor-retries', '1', url]
    try:
        result = subprocess.run(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                timeout=35, shell=False, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    except subprocess.TimeoutExpired as error:
        raise ValueError('No se pudo analizar el enlace en 35 segundos.') from error
    if result.returncode != 0:
        diagnostic = result.stderr.decode('utf-8', errors='replace')[-700:]
        raise ValueError(friendly_error(diagnostic))
    if len(result.stdout) > MAX_PREVIEW:
        raise ValueError('El sitio devolvió demasiados metadatos.')
    try:
        data = json.loads(result.stdout.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError('No se pudieron interpretar los datos del sitio.') from error
    return simplify_metadata(data)


def terminate_tree(process):
    if process.poll() is not None:
        return
    if os.name == 'nt':
        try:
            subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                           stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, timeout=5, shell=False,
                           creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            return
        except (OSError, subprocess.TimeoutExpired):
            pass
    try:
        process.terminate()
    except OSError:
        pass


def run_ytdlp(args, attempt, total, cancel_event=None):
    last_error = ''
    output = ''
    was_cancelled = False
    last_emit = 0.0
    last_percent = -1.0
    send({'type': 'progress', 'percent': 0, 'stage': 'download',
          'message': f'Conectando al sitio · intento {attempt}/{total}…'})
    finished = threading.Event()
    flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
    with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          stdin=subprocess.DEVNULL, encoding='utf-8', errors='replace',
                          bufsize=1, shell=False, creationflags=flags) as process:
        def watcher():
            while not finished.wait(0.15):
                if cancel_event is not None and cancel_event.is_set():
                    terminate_tree(process)
                    return
        monitor = threading.Thread(target=watcher, daemon=True)
        monitor.start()
        try:
            for raw in process.stdout:
                line = ANSI.sub('', raw.strip())
                if not line:
                    continue
                if line.startswith('APEX_OUTPUT:'):
                    output = line[len('APEX_OUTPUT:'):].strip()
                if line.startswith('ERROR:'):
                    last_error = line[6:].strip()[:600]
                if any(token in line for token in ('[download]', '[Merger]', '[ExtractAudio]', '[VideoConvertor]')):
                    match = PERCENT.search(line)
                    progress = max(0, min(99, float(match.group(1)))) if match else None
                    processing = any(t in line for t in ('[Merger]', '[ExtractAudio]', '[VideoConvertor]'))
                    now = time.monotonic()
                    if not processing and progress is not None and now - last_emit < 0.4 and abs(progress - last_percent) < 1.0:
                        continue
                    last_emit = now
                    if progress is not None:
                        last_percent = progress
                    send({'type': 'progress', 'percent': progress,
                          'stage': 'processing' if processing else 'download',
                          'message': 'Combinando o convirtiendo con FFmpeg…' if processing else line[:230]})
            code = process.wait()
        finally:
            finished.set()
            monitor.join(timeout=0.5)
        was_cancelled = bool(cancel_event and cancel_event.is_set())
    return code, last_error, output, was_cancelled


def download(request, listen_for_cancel=True):
    url = validate_url(request.get('url'))
    media_format = request.get('format')
    quality = request.get('quality')
    mode = request.get('mode', 'stable')
    if media_format not in ('mp3', 'mp4') or quality not in ALLOWED_QUALITY or mode not in ALLOWED_MODE:
        raise ValueError('Formato, calidad o compatibilidad inválidos.')
    if not ytdlp_version():
        raise ValueError('Falta yt-dlp. Repara la instalación local.')
    has_ffmpeg = bool(shutil.which('ffmpeg'))
    if media_format == 'mp3' and not has_ffmpeg:
        raise ValueError('Se necesita FFmpeg para convertir a MP3.')
    destination = folder()
    if destination != default_folder() and not destination.is_dir():
        raise ValueError('La carpeta elegida ya no está disponible. Cambia la ruta en Apex Descarga.')
    destination.mkdir(parents=True, exist_ok=True)
    cancel_event = threading.Event()

    def listen_cancel():
        # Keep receiving framed commands while yt-dlp runs; only "cancel" is accepted.
        try:
            while True:
                message = recv()
                if message is None:
                    cancel_event.set()
                    return
                if message.get('type') == 'cancel':
                    cancel_event.set()
                    return
        except (ValueError, EOFError, OSError, json.JSONDecodeError):
            cancel_event.set()

    if listen_for_cancel:
        threading.Thread(target=listen_cancel, daemon=True).start()
    modes = [mode]
    if media_format == 'mp4' and has_ffmpeg and mode == 'stable':
        modes.append('compatible')
    raw_error = ''
    output = ''
    for index, choice in enumerate(modes, 1):
        if cancel_event.is_set():
            break
        args = build_args(url, media_format, quality, choice, has_ffmpeg)
        code, raw_error, found_path, cancelled = run_ytdlp(args, index, len(modes), cancel_event)
        output = found_path or output
        if cancelled:
            cancel_event.set()
        if cancelled or cancel_event.is_set():
            break
        if code == 0:
            send({'type': 'done', 'ok': True, 'folder': str(folder()),
                  'file': Path(output).name if output else '', 'message': 'Descarga completada.'})
            return
        if not ('403' in raw_error.lower() and index < len(modes)):
            break
        send({'type': 'progress', 'percent': None, 'stage': 'retry',
              'message': 'HTTP 403: probando transporte alternativo…'})
    if cancel_event.is_set():
        send({'type': 'done', 'ok': False, 'cancelled': True, 'folder': str(folder()),
              'error': 'Descarga cancelada por el usuario.'})
    else:
        send({'type': 'done', 'ok': False, 'folder': str(folder()),
              'error': friendly_error(raw_error), 'technical': raw_error[:500]})


def open_folder():
    directory = folder()
    directory.mkdir(parents=True, exist_ok=True)
    if sys.platform != 'win32':
        raise ValueError('Esta función requiere Windows.')
    os.startfile(str(directory))
    return {'type': 'open_folder', 'ok': True}


def main():
    try:
        request = recv()
        if request is None:
            return
        action = request.get('type')
        if action == 'status':
            send(status())
        elif action == 'preview':
            send(preview(validate_url(request.get('url'))))
        elif action == 'open_folder':
            send(open_folder())
        elif action == 'choose_folder':
            send(choose_folder())
        elif action == 'download':
            download(request)
        else:
            send({'type': 'error', 'error': 'Operación desconocida.'})
    except (ValueError, OSError, EOFError, json.JSONDecodeError) as error:
        send({'type': 'error', 'error': str(error)[:500]})
    except Exception:
        send({'type': 'error', 'error': 'Error interno del componente local.'})


if __name__ == '__main__':
    main()
