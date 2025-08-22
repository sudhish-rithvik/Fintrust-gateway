@echo off
title FinTrust Gateway - All Services

echo 🚀 Starting FinTrust Gateway Services...
echo ========================================

echo.
echo Starting Backend (Port 8000)...
start "Backend" cmd /k "cd backend\\app && python main.py"

timeout /t 3 /nobreak > nul

echo Starting Encryption Service (Port 5000)...  
start "Encryption" cmd /k "cd encryption-service && python app.py"

timeout /t 3 /nobreak > nul

echo Starting Frontend (Port 3000)...
start "Frontend" cmd /k "cd frontend && npm start"

echo.
echo ✅ All services are starting!
echo.
echo Services will open in separate windows:
echo - Backend API: http://localhost:8000/docs
echo - Frontend: http://localhost:3000  
echo - Encryption: http://localhost:5000/health
echo.
echo Press any key to exit this window...
pause > nul
