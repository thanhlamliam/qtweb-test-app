#  cSpell:disable 

import sys
import asyncio
import urllib.parse
import os
import winreg
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit,
    QPushButton, QHBoxLayout, QMessageBox, QLineEdit
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QThread, Signal, QObject, Qt
from browser_use import Agent, BrowserConfig, Browser
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv()

# Global variable
global_api_key = ""

# Định nghĩa style chung
STYLESHEET = """
    QWidget { padding: 10px; }
    QTextEdit {
        padding: 8px; font-size: 14px; border: 2px solid #ccc;
        border-radius: 5px; background-color: #fff; color: #000;
    }
    QTextEdit:focus { border: 2px solid #0078d7; }
    QPushButton {
        padding: 10px; font-size: 14px; font-weight: bold; color: white;
        border: none; border-radius: 5px;
    }
    QPushButton { background-color: #0078d7; }
    QPushButton:hover { background-color: #005bb5; }
    QPushButton:pressed { background-color: #003087; }
    QPushButton#stop { background-color: #d70000; }
    QPushButton#stop:hover { background-color: #b50000; }
    QPushButton#stop:pressed { background-color: #870000; }
    QPushButton:disabled { background-color: #cccccc; color: #666666; }
"""

class WorkerSignals(QObject):
    finished = Signal(str)
    error = Signal(str)

class AITaskWorker(QThread):
    def __init__(self, chrome_path, chrome_user_data, api_key, task):
        super().__init__()
        self.chrome_path = chrome_path
        self.chrome_user_data = chrome_user_data
        self.api_key = api_key
        self.task = task
        self.signals = WorkerSignals()
        self.browser = None
        self.agent = None

    async def _run_agent(self):
        extra_chromium_args = [
            "--window-size=800,600",
            f"--user-data-dir={self.chrome_user_data}",
            "--no-first-run",              # Tránh hiển thị màn hình chào mừng
            "--no-default-browser-check",  # Không kiểm tra trình duyệt mặc định
            "--new-window"                 # Đảm bảo mở cửa sổ mới (không ảnh hưởng Chrome đang chạy)
        ]
        config = BrowserConfig(
            chrome_instance_path=self.chrome_path,
            extra_chromium_args=extra_chromium_args,
        )
        
        self.browser = Browser(config=config)
        
        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp", 
                google_api_key=SecretStr(self.api_key)
            )
        except Exception as e:
            raise ValueError(f"Không khởi tạo được model: {str(e)}")

        self.agent = Agent(task=self.task, llm=llm, browser=self.browser)
        return await self.agent.run()

    def run(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._run_agent())
            self.signals.finished.emit("Task completed")
        except Exception as e:
            self.signals.error.emit(f"Error: {str(e)}")

    def stop(self):
        if self.agent:
            self.agent.stop()

class BrowserWindow(QMainWindow):
    DEFAULT_CHROME_PATH = os.getenv("ProgramFiles", "C:/Program Files") + "/Google/Chrome/Application/chrome.exe"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PTEE AI Agent")
        self.setGeometry(100, 100, 1000, 600)
        self.worker = None
        self._setup_ui()
        self._handle_url_protocol()

    def _setup_ui(self):
        self.setStyleSheet(STYLESHEET)

        self.browser = QWebEngineView()
        self.task_input = QTextEdit(placeholderText="Enter AI task")

        self.run_button = QPushButton("Run AI")
        self.run_button.setObjectName("run")
        self.run_button.clicked.connect(self._run_ai_task)

        self.stop_button = QPushButton("Stop AI")
        self.stop_button.setObjectName("stop")
        self.stop_button.clicked.connect(self._stop_agent)

        layout = QVBoxLayout()
        layout.addWidget(self.task_input)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.run_button, 2)
        button_layout.addWidget(self.stop_button, 1)
        layout.addLayout(button_layout)
        layout.addWidget(self.browser)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def _handle_url_protocol(self):
        global global_api_key
        if len(sys.argv) > 1:
            url = sys.argv[1]
            apikey, task = self._parse_url_protocol(url)
            if apikey and task:
                global_api_key = apikey
                self.task_input.setPlainText(task)
                self._run_ai_task(apikey=apikey)

    @staticmethod
    def _get_registry_value(value_name):
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "PTEEAIAgent\\Settings") as key:
                return winreg.QueryValueEx(key, value_name)[0]
        except:
            return None

    @staticmethod
    def _parse_url_protocol(url):
        if not url.startswith("pteeaiagent://"):
            return None, None
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        apikey = query_params.get("apikey", [None])[0]
        task = query_params.get("task", [None])[0]
        return apikey, task

    def _run_ai_task(self, apikey=None):
        chrome_path = self._get_registry_value("ChromeExePath") or self.DEFAULT_CHROME_PATH
        chrome_user_data = self._get_registry_value("ChromeUserDataPath")
        api_key = apikey or global_api_key
        task = self.task_input.toPlainText()

        if not chrome_user_data:
            QMessageBox.information(self, "Error", "Chrome User Data path not found in registry")
            return
        if not os.path.exists(chrome_path):
            QMessageBox.information(self, "Error", f"Chrome not found at {chrome_path}")
            return
        if not api_key:
            QMessageBox.information(self, "Error", "API key not provided")
            return
        if not task:
            QMessageBox.information(self, "Error", "Please enter a task")
            return

        self.run_button.setEnabled(False)
        self.worker = AITaskWorker(chrome_path, chrome_user_data, api_key, task)
        self.worker.signals.finished.connect(self._on_task_finished)
        self.worker.signals.error.connect(self._on_task_error)
        self.worker.start()

    def _stop_agent(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            QMessageBox.information(self, "Stop", "Stop requested - agent will halt at next safe point")

    def _on_task_finished(self, message):
        self.run_button.setEnabled(True)
        QMessageBox.information(self, "Success", message)

    def _on_task_error(self, error_message):
        self.run_button.setEnabled(True)
        QMessageBox.warning(self, "Error", error_message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BrowserWindow()
    window.show()
    sys.exit(app.exec())