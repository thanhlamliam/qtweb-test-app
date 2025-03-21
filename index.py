import sys
import asyncio
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QTextEdit,
    QPushButton,
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from browser_use import Agent, BrowserConfig, Browser
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from pydantic import SecretStr
import os

load_dotenv()  # Load API key from .env


class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Browser with PySide6")
        self.setGeometry(100, 100, 800, 600)

        # Set up browser
        self.browser = QWebEngineView()

        # Input for AI task
        self.task_input = QTextEdit()
        self.task_input.setPlaceholderText("Enter AI task (e.g., 'Search for dogs')")

        # Button to trigger AI
        self.run_button = QPushButton("Run AI")
        self.run_button.clicked.connect(self.run_ai_task)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.task_input)
        layout.addWidget(self.run_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    async def run_agent(self, task):
        extra_chromium_args = [f"--window-size={1200},{1200}"]
        chrome_path = os.getenv("CHROME_PATH", None)
        if chrome_path == "":
            chrome_path = None
        chrome_user_data = os.getenv("CHROME_USER_DATA", None)
        if chrome_user_data:
            extra_chromium_args += [f"--user-data-dir={chrome_user_data}"]
            
        # Basic configuration
        config = BrowserConfig(
            chrome_instance_path=chrome_path,
            extra_chromium_args=extra_chromium_args
        )

        browser = Browser(config=config)
        
        # Initialize the model
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY không được tìm thấy trong .env")
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",  # Đảm bảo model này tồn tại
            google_api_key=SecretStr(api_key)  # Sửa tham số thành google_api_key
        )

        # Create agent with the model
        agent = Agent(task=task, llm=llm, browser=browser)
        result = await agent.run()

        return result

    def run_ai_task(self):
        task = self.task_input.toPlainText()
        if task:
            # Run async task in Qt event loop
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.run_agent(task))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BrowserWindow()
    window.show()
    sys.exit(app.exec())
