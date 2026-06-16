@echo off
title Recess Bites Canteen Management System

echo.
echo ====================================================
echo    RECESS BITES CANTEEN MANAGEMENT SYSTEM
echo ====================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

:: Check if pip is available
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip is not available
    echo Please install pip and try again
    pause
    exit /b 1
)

echo ✅ Python found, checking dependencies...

:: Install required packages if they don't exist
echo 📦 Installing/checking required packages...
pip install flask mysql-connector-python yagmail werkzeug

if %errorlevel% neq 0 (
    echo ❌ Failed to install required packages
    pause
    exit /b 1
)

echo.
echo ✅ All dependencies installed successfully!
echo.

:: Run the configuration check first
echo 🔍 Validating configuration...
python config.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Configuration validation failed
    echo Please check your config.py file and database settings
    pause
    exit /b 1
)

echo.
echo 🚀 Starting Recess Bites Server...
echo.
echo 💡 Access the application at:
echo    👉 http://localhost:5000
echo.
echo 📌 Admin Login:
echo    Email: recessbites4@gmail.com  
echo    Password: 12332112
echo.
echo 🔧 To stop the server, press Ctrl+C
echo.

:: Start the Flask application
python app.py

echo.
echo 👋 Server stopped. Press any key to exit...
pause