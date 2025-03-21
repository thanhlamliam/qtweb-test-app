# NOTE: Python version >= 3.11

```bash
python -m venv venv # Or `uv venv --python 3.11` if you are using uv
.venv/Script/activate

pip install browser-use
playwright install
pip install langchain_google_genai PySide6

py main.py
```

# Clear cache

```bash
pip cache purge
uv cache clean
```

# Format: Black Formatter