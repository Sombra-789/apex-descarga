#!/usr/bin/env python3
"""Smoke-tests version parsing, YouTube art and Wi-Fi logic with minimal Android stubs.
This is NOT a substitute for Android Gradle compilation on a device.
"""
from pathlib import Path
import tempfile, subprocess
root=Path(__file__).resolve().parents[1]
# Tests are included as source files under scripts/java_smoke
stub=root/'scripts/java_smoke'
original=root/'app/src/main/java/com/apexvisualstudio/descarga'
with tempfile.TemporaryDirectory() as td:
    java=[str(p) for p in stub.rglob('*.java')]
    java += [str(original/(n+'.java')) for n in ['NetworkPolicy','MediaMetadata','EngineHealth']]
    subprocess.run(['javac','--release','17','-d',td,*java],check=True)
    subprocess.run(['java','-cp',td,'com.apexvisualstudio.descarga.SmokeTest'],check=True)
