import PyInstaller.__main__
import os
import shutil

# 1. Clean previous build
if os.path.exists("dist"): shutil.rmtree("dist")
if os.path.exists("build"): shutil.rmtree("build")

# 2. Run PyInstaller
PyInstaller.__main__.run([
    'src/main.py',
    '--name=OGT_WatchTower_V3',
    '--onefile',
    '--windowed',
    '--uac-admin',
    # '--icon=assets/folderico-NZHQZR.ico',
    '--add-data=config;config',  # Include config folder
    '--add-data=C:/Users/OGT/AppData/Local/Programs/Python/Python312/Lib/site-packages/customtkinter;customtkinter/',
    # '--add-data=assets;assets', # Include assets if needed
    '--hidden-import=win32timezone',
    '--hidden-import=PIL._tkinter_finder',
    '--hidden-import=yaml',
    '--clean',
])

# 3. Move to release folder
if not os.path.exists("release"):
    os.makedirs("release")

src_exe = "dist/OGT_WatchTower_V3.exe"
dst_exe = "release/OGT_WatchTower_V3.exe"


if os.path.exists(src_exe):
    shutil.move(src_exe, dst_exe)
    print(f"[+] Build Success! Executable is in: {dst_exe}")
else:
    print("[-] Build Failed. Executable not found.")
