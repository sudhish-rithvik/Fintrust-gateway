@echo off
echo 🚀 FinTrust Gateway - Local Setup Script
echo ========================================

echo.
echo 📁 Setting up directories...
if not exist "backend\app" mkdir "backend\app"
if not exist "backend\app\routes" mkdir "backend\app\routes"
if not exist "frontend\src" mkdir "frontend\src"
if not exist "frontend\public" mkdir "frontend\public"
if not exist "encryption-service" mkdir "encryption-service"

echo.
echo 📝 Creating Python virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo.
echo 📦 Installing backend dependencies...
pip install fastapi==0.111.0 uvicorn[standard]==0.29.0 requests==2.32.3 python-jose[cryptography]==3.3.0 python-dotenv==1.0.1 pydantic-settings==2.4.0 python-multipart==0.0.9

echo.
echo 📦 Installing encryption service dependencies...  
pip install flask==3.0.3 flask-cors==4.0.1 cryptography==41.0.7

echo.
echo 🌐 Installing frontend dependencies...
cd frontend
call npm install
call npm install axios
cd ..

echo.
echo ✅ Setup complete!
echo.
echo To run the application:
echo 1. Backend: cd backend\app ^&^& python main.py
echo 2. Frontend: cd frontend ^&^& npm start  
echo 3. Encryption: cd encryption-service ^&^& python app.py
echo.
echo Or use run-all.bat to start everything at once!
pause
