#!/usr/bin/env python3
"""Parse Android Java sources with javac's compiler frontend (without Android SDK)."""
from pathlib import Path
import tempfile,subprocess
r=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as td:
    subprocess.run(['javac','--release','17','-d',td,str(r/'scripts/SyntaxCheck.java')],check=True)
    subprocess.run(['java','-cp',td,'SyntaxCheck',str(r/'app/src/main/java')],check=True)
