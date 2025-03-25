import os
import shutil
import winreg
import sys
import subprocess

APP_NAME = "PTEEAIAgent"
REGISTRY_PATH = f"Software\\{APP_NAME}"
PROTOCOL_NAME = "PTEEAIAgent"


def remove_registry():
    """Xóa các key registry liên quan đến ứng dụng."""
    try:
        # Xóa key trong HKEY_CLASSES_ROOT
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, f"{APP_NAME}\\Settings")
        print(f"Đã xóa registry: HKCR\\{APP_NAME}\\Settings")
    except FileNotFoundError:
        print(f"Không tìm thấy registry: HKCR\\{APP_NAME}\\Settings")
    except Exception as e:
        print(f"Lỗi khi xóa HKCR registry: {str(e)}")

    try:
        # Xóa key URL Protocol trong HKEY_CLASSES_ROOT
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, f"{PROTOCOL_NAME}\\shell\\open\\command")
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, f"{PROTOCOL_NAME}\\shell\\open")
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, f"{PROTOCOL_NAME}\\shell")
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, PROTOCOL_NAME)
        print(f"Đã xóa URL Protocol: HKCR\\{PROTOCOL_NAME}")
    except FileNotFoundError:
        print(f"Không tìm thấy URL Protocol: HKCR\\{PROTOCOL_NAME}")
    except Exception as e:
        print(f"Lỗi khi xóa HKCR registry: {str(e)}")


def remove_files(app_dir):
    """Xóa thư mục cài đặt ứng dụng."""
    if os.path.exists(app_dir):
        try:
            shutil.rmtree(app_dir)
            print(f"Đã xóa thư mục: {app_dir}")
        except Exception as e:
            print(f"Lỗi khi xóa thư mục {app_dir}: {str(e)}")
    else:
        print(f"Không tìm thấy thư mục: {app_dir}")


def remove_shortcuts():
    """Xóa shortcut trên Desktop và Start Menu."""
    desktop_path = os.path.join(os.environ["USERPROFILE"], "Desktop", f"{APP_NAME}.lnk")
    start_menu_path = os.path.join(
        os.environ["APPDATA"],
        "Microsoft",
        "Windows",
        "Start Menu",
        "Programs",
        APP_NAME,
    )

    if os.path.exists(desktop_path):
        os.remove(desktop_path)
        print(f"Đã xóa shortcut Desktop: {desktop_path}")

    if os.path.exists(start_menu_path):
        shutil.rmtree(start_menu_path)
        print(f"Đã xóa Start Menu folder: {start_menu_path}")


def main():
    # Đường dẫn mặc định của ứng dụng
    app_dir = os.path.join(os.environ["ProgramFiles"], APP_NAME)

    print(f"Bắt đầu gỡ cài đặt {APP_NAME}...")

    # Xóa file, registry, và shortcut
    remove_files(app_dir)
    remove_registry()
    remove_shortcuts()

    print(f"Đã gỡ cài đặt {APP_NAME} thành công!")

    # Tự xóa uninstaller sau khi hoàn tất (tùy chọn)
    if "--self-delete" in sys.argv:
        subprocess.Popen(f'cmd.exe /c del "{sys.argv[0]}"', shell=True)


if __name__ == "__main__":
    main()
