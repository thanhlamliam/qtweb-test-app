#  cSpell:disable 

# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Thu thập tất cả file dữ liệu cần thiết
datas = (
    collect_data_files("PySide6", include_py_files=True) +           # PySide6 và file Python
    collect_data_files("PySide6.QtWebEngine", include_py_files=True) +  # Qt WebEngine
    collect_data_files("browser_use", include_py_files=True) +       # Browser-Use
    collect_data_files("playwright", include_py_files=True) +        # Playwright
    collect_data_files("langchain_openai", include_py_files=True) +  # LangChain OpenAI
    collect_data_files("dotenv", include_py_files=True) +            # Dotenv
    collect_data_files("requests", include_py_files=True) +          # Requests (cho SSL)
    collect_data_files("pydantic", include_py_files=True)            # Pydantic
)

# Bao gồm tất cả module ẩn
hidden_imports = (
    collect_submodules("PySide6") +             # Tất cả module PySide6
    collect_submodules("browser_use") +         # Tất cả module Browser-Use
    collect_submodules("playwright") +          # Tất cả module Playwright
    collect_submodules("langchain_openai") +    # Tất cả module LangChain OpenAI
    collect_submodules("pydantic") +            # Tất cả module Pydantic
    collect_submodules("requests") +            # Tất cả module Requests
    collect_submodules("dotenv") +              # Tất cả module Dotenv
    [
        'asyncio',
        'PySide6.QtWebEngineCore',
        'pydantic.deprecated.decorator',
        'playwright.async_api',
        'requests.adapters',
    ]
)

# Cấu hình đóng gói
a = Analysis(
    ['ai-agent.py'],  # File chính của ứng dụng
    pathex=[],
    binaries=[],  # Thêm QtWebEngineProcess.exe
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],  # Không loại trừ gì để đảm bảo đầy đủ
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None
)

# Tạo file .pyz (nén code Python)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Tạo file .exe duy nhất
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='PTEEAIAgent',
    debug=False,
    strip=False,
    upx=True,
    console=True  # Giữ console để kiểm tra lỗi
)