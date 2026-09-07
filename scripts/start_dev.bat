@echo off
echo Starting Cloud FinOps AI...
echo.

echo [1/2] Starting Backend on http://localhost:8000
start "Backend" cmd /k "cd /d D:\Cloud-Finops-AI\backend && D:\Cloud-Finops-AI\.venv\Scripts\uvicorn.exe app.main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] Starting Frontend on http://localhost:5173
start "Frontend" cmd /k "cd /d D:\Cloud-Finops-AI\frontend && npm run dev"

echo.
echo Both servers starting...
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo Swagger:  http://localhost:8000/docs
echo.
pause
