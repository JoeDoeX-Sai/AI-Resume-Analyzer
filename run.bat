@echo off
REM Quick start script for Windows

echo Starting AI Resume Analyzer...
echo.

REM Start backend
echo Starting backend server...
start cmd /k "cd backend && venv\Scripts\activate.bat && python app.py"

REM Wait a bit for backend to start
timeout /t 3 /nobreak > nul

REM Start frontend
echo Starting frontend...
start cmd /k "cd frontend && python -m http.server 8000"

REM Wait a bit
timeout /t 2 /nobreak > nul

REM Open browser
echo Opening browser...
start http://localhost:8000

echo.
echo AI Resume Analyzer is running!
echo Backend: http://localhost:5000
echo Frontend: http://localhost:8000
echo.
echo Press any key to stop all servers...
pause > nul

REM Kill servers
taskkill /F /FI "WindowTitle eq *backend*" /T > nul 2>&1
taskkill /F /FI "WindowTitle eq *frontend*" /T > nul 2>&1
