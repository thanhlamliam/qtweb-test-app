# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['uninstaller.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['winreg', 'shutil', 'subprocess'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='PTEEAIAgentUninstaller',
    debug=False,
    strip=False,
    upx=True,
    console=True
)