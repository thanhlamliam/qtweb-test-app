import sys
import asyncio
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QGridLayout,
    QWidget,
    QTextEdit,
    QPushButton,
    QLabel,
    QLineEdit,
    QMessageBox,
    QHBoxLayout
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import Qt, QThread, Signal, QObject
from browser_use import Agent, BrowserConfig, Browser
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv()

# Global variables for persistence
_global_browser = None
_global_agent = None


class WorkerSignals(QObject):
    finished = Signal(str)  # Signal khi hoàn thành
    error = Signal(str)  # Signal khi có lỗi


class AITaskWorker(QThread):
    def __init__(self, loc_chrome, loc_chrome_user_dt, api_key, task):
        super().__init__()
        self.loc_chrome = loc_chrome
        self.loc_chrome_user_dt = loc_chrome_user_dt
        self.api_key = api_key
        self.task = task
        self.signals = WorkerSignals()

    async def run_agent(self):
        global _global_browser, _global_agent
        extra_chromium_args = [f"--window-size={800},{600}"]
        extra_chromium_args += [f"--user-data-dir={self.loc_chrome_user_dt}"]

        config = BrowserConfig(
            chrome_instance_path=self.loc_chrome,
            extra_chromium_args=extra_chromium_args,
        )

        _global_browser = Browser(config=config)

        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp", google_api_key=SecretStr(self.api_key)
            )
        except Exception as e:
            raise ValueError(f"ERROR: Không khởi tạo được model - {str(e)}")

        _global_agent = Agent(task=self.task, llm=llm, browser=_global_browser)
        result = await _global_agent.run()
        return result

    def run(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.run_agent())
            self.signals.finished.emit(f"Task completed")
            return result
        except Exception as e:
            self.signals.error.emit(f"Error: {str(e)}")


class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Browser with PySide6")
        self.setGeometry(100, 100, 1000, 600)

        self.setStyleSheet(
            """
            QWidget { 
                padding: 10px; 
            }
            QLabel { 
                font-size: 16px;
                font-weight: 600;
            }
            QLineEdit, QTextEdit {
                padding: 8px;
                font-size: 14px;
                border: 2px solid #ccc;
                border-radius: 5px;
                background-color: #fff;
                color: #000;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 2px solid #0078d7;
            }
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                color: white;
                background-color: #0078d7;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005bb5;
            }
            QPushButton:pressed {
                background-color: #003087;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            """
        )

        self.browser = QWebEngineView()

        loc_chrome = QLabel("Location of Chrome app:")
        self.loc_chrome_input = QLineEdit()
        self.loc_chrome_input.setPlaceholderText(
            "e.g., C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        )

        loc_chrome_user_data = QLabel("Location of Chrome user data:")
        self.loc_chrome_user_data_input = QLineEdit()
        self.loc_chrome_user_data_input.setPlaceholderText(
            "e.g., C:\\Users\\<Username>\\AppData\\Local\\Google\\Chrome\\User Data"
        )

        api_key_label = QLabel("API Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter API key")

        task_label = QLabel("Task:")
        self.task_area = QTextEdit()
        self.task_area.setFixedHeight(200)
        self.task_area.setPlaceholderText("Enter AI task")

        self.run_button = QPushButton("Run AI")
        self.run_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.run_button.clicked.connect(self.run_ai_task)

        self.stop_button = QPushButton("Stop AI")
        self.stop_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_button.clicked.connect(self.stop_agent)

        layout = QGridLayout()
        layout.addWidget(loc_chrome, 0, 0)
        layout.addWidget(self.loc_chrome_input, 0, 1)
        layout.addWidget(loc_chrome_user_data, 1, 0)
        layout.addWidget(self.loc_chrome_user_data_input, 1, 1)
        layout.addWidget(api_key_label, 2, 0)
        layout.addWidget(self.api_key_input, 2, 1)
        layout.addWidget(task_label, 3, 0, Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.task_area, 3, 1)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout, 4, 1)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.worker = None  # Lưu trữ worker thread

    def run_ai_task(self):
        loc_chrome = self.loc_chrome_input.text()
        loc_chrome_data = self.loc_chrome_user_data_input.text()
        api_key = self.api_key_input.text()
        task = self.task_area.toPlainText()

        if not loc_chrome:
            loc_chrome = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

        if not loc_chrome_data:
            QMessageBox.information(
                self, "Empty Field", "Please enter location of Chrome user data"
            )
            return
        if not api_key:
            QMessageBox.information(
                self, "Empty Field", "Please enter API Key for Gemini Model 2.0 Flash"
            )
            return
        if not task:
            QMessageBox.information(self, "Empty Field", "Please enter task")
            return

        # Chạy task trong thread riêng
        # self.run_button.setCursor(Qt.CursorShape.ForbiddenCursor)
        self.run_button.setEnabled(False)  # Vô hiệu hóa nút Run khi đang chạy
        self.worker = AITaskWorker(loc_chrome, loc_chrome_data, api_key, task)
        self.worker.signals.finished.connect(self.on_task_finished)
        self.worker.signals.error.connect(self.on_task_error)
        self.worker.start()

    def stop_agent(self):
        global _global_agent
        if _global_agent:
            try:
                _global_agent.stop()
                QMessageBox.information(
                    self, "Stop", "Stop requested - agent will halt at next safe point"
                )
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error during stop: {str(e)}")

    def on_task_finished(self, message):
        self.run_button.setEnabled(True)
        QMessageBox.information(self, "Success", message)

    def on_task_error(self, error_message):
        self.run_button.setEnabled(True)
        QMessageBox.warning(self, "Error", error_message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BrowserWindow()
    window.show()
    sys.exit(app.exec())
