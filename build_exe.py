"""Build script for Music Player Pro
Generates a one‑file Windows executable using PyInstaller.
Runs with the current Python environment (must have all runtime
requirements installed, including pyinstaller).
"""
import subprocess
import sys
import os

def run_cmd(cmd):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        sys.exit(result.returncode)

# Path to the main entry point
entry = os.path.join(os.path.dirname(__file__), 'main.py')

# Build options
opts = [
    'pyinstaller',
    '--name', 'MusicPlayerPro',
    '--onefile',            # single executable
    '--windowed',           # no console window
    '--add-data', f"icon.ico;.",
    '--add-data', f"icon.png;.",
    '--add-data', f"ui{os.pathsep}ui",
    '--add-data', f"core{os.pathsep}core",
    '--add-data', f"services{os.pathsep}services",
    '--add-data', f"utils{os.pathsep}utils",
    entry,
]

run_cmd(opts)

print('Build finished. Executable is in ./dist/')
