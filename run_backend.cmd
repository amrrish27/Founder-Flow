@echo off
cd /d "%~dp0backend"
if not exist venv python -m venv venv
echo Installing requirements...
venv\Scripts\python.exe -m pip install -r requirements.txt
echo Starting FastAPI server...
venv\Scripts\python.exe -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
pause
