#  cSpell:disable 

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
from PySide6.QtCore import Qt
from browser_use import Agent, BrowserConfig, Browser
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv()  # Load API key from .env

# Global variables for persistence
_global_browser = None
_global_agent = None

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
        """
        )

        # Set up browser
        self.browser = QWebEngineView()

        # Input for Chrome exe
        loc_chrome = QLabel("Location of Chrome app:")
        self.loc_chrome_input = QLineEdit()
        self.loc_chrome_input.setPlaceholderText(
            "Enter location of Chrome app (e.g., C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe)"
        )

        # Input for Chrome User Data
        loc_chrome_user_data = QLabel("Location of Chrome user data:")
        self.loc_chrome_user_data_input = QLineEdit()
        self.loc_chrome_user_data_input.setPlaceholderText(
            "Enter location of Chrome user data (e.g., C:\\Users\\<Username>\\AppData\\Local\\Google\\Chrome\\User Data)"
        )

        # Input for API Key
        api_key_label = QLabel("API Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter API key")

        # Input for AI task
        task_label = QLabel("Task:")
        self.task_area = QTextEdit()
        self.task_area.setFixedHeight(200)
        self.task_area.setPlaceholderText("Enter AI task")

        # Button to trigger AI
        self.run_button = QPushButton("Run AI")
        self.run_button.clicked.connect(self.run_ai_task)
        
        # Button to stop AI
        self.stop_button = QPushButton("Stop AI")
        self.stop_button.clicked.connect(self.stop_agent)

        # Layout
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

    async def run_agent(self, loc_chrome, loc_chrome_user_dt, api_key, task):
        global _global_browser, _global_agent
        extra_chromium_args = [f"--window-size={800},{600}"]
        extra_chromium_args += [f"--user-data-dir={loc_chrome_user_dt}"]

        # Basic configuration
        config = BrowserConfig(
            chrome_instance_path=loc_chrome, extra_chromium_args=extra_chromium_args
        )

        _global_browser = Browser(config=config)

        # Initialize the model
        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp", google_api_key=SecretStr(api_key)
            )
        except:
            raise ValueError("ERROR: An exception occurred")

        # Create agent with the model
        _global_agent = Agent(task=task, llm=llm, browser=_global_browser)
        result = await _global_agent.run()

        return result

    async def stop_agent():
        global _global_agent_state, _global_browser_context, _global_browser, _global_agent
        try:
            # Request stop
            _global_agent.stop()
            message = "Stop requested - the agent will halt at the next safe point"
            return message
        except Exception as e:
            error_msg = f"Error during stop: {str(e)}"
            return error_msg

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

        # Run async task in Qt event loop
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self.run_agent(loc_chrome, loc_chrome_data, api_key, task)
        )



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BrowserWindow()
    window.show()
    sys.exit(app.exec())
