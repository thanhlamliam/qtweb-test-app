#  cSpell:disable 

# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = (
    collect_data_files("PySide6", include_py_files=True) +
    collect_data_files("PySide6.QtWebEngine", include_py_files=True) +
    collect_data_files("browser_use", include_py_files=True) +
    collect_data_files("langchain_google_genai", include_py_files=True) +
    collect_data_files("requests", include_py_files=True) +
    collect_data_files("dotenv", include_py_files=True) +
    collect_data_files("urllib3", include_py_files=True) +
    collect_data_files("playwright", include_py_files=True) +
    collect_data_files("pydantic", include_py_files=True) 
)

hidden_imports = (
    collect_submodules("PySide6") +
    collect_submodules("browser_use") +
    collect_submodules("langchain_google_genai") +
    collect_submodules("requests") +
    collect_submodules("dotenv") +
    collect_submodules("urllib3") +
    collect_submodules("playwright") +
    collect_submodules("pydantic") +
    [
        "asyncio",
        "PySide6.QtWebEngineCore",
        "requests.adapters",
        "google.api_core",
        "playwright.async_api",
        'pydantic.deprecated.decorator',
    ]
)

a = Analysis(
    ["ai-agent-v3.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
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
    name="PTEEAIAgent",
    debug=True,
    strip=False,
    upx=True,
    console=True
)