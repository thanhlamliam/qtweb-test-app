# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

# Thu thập file dữ liệu của PySide6 và Qt WebEngine
datas = collect_data_files("PySide6")
datas += collect_data_files("PySide6.QtWebEngine")
datas += collect_data_files("browser_use")
datas += collect_data_files("playwright")
datas += [(".env", ".")]  # Thêm file .env nếu bạn dùng để lưu API key

# Cấu hình đóng gói
a = Analysis(
    ['index.py'],  # File chính của ứng dụng
    pathex=[],  # Đường dẫn thêm nếu cần (thường để trống)
    binaries=[],  # File nhị phân thêm (thường để PyInstaller tự tìm)
    datas=datas,  # Các file dữ liệu cần đóng gói
    hiddenimports=[
        'browser_use', 
        'langchain_openai', 
        'asyncio', 
        'PySide6.QtWebEngineCore', 
        'pydantic.deprecated.decorator', 
        'pydantic',
        'playwright',              # Thêm Playwright
        'playwright.async_api'     # Module async của Playwright
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],  # Module không cần đóng gói (để trống nếu không chắc)
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None  # Không mã hóa (giữ mặc định)
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
    name='AIBrowser',  # Tên file .exe
    debug=False,       # Không bật chế độ debug
    strip=False,       # Không loại bỏ symbol (giữ nguyên để tránh lỗi)
    upx=True,          # Nén file nếu có UPX (tùy chọn)
    console=True       # Hiển thị console để xem lỗi (có thể đổi thành False sau)
)