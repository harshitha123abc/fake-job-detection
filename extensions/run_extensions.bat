@echo off
REM Direct Access Extensions Launcher (Windows)
REM This script helps you quickly test all the direct access interfaces

echo 🚀 Fake Job Detection - Direct Access Extensions
echo ================================================
echo.

REM Check if API is running
echo 📡 Checking if Flask API is running...
curl -s http://localhost:5000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ API is running on http://localhost:5000
) else (
    echo ❌ API is not running. Please start it with: python api.py
    echo.
    echo Starting API...
    start /B python api.py
    timeout /t 3 /nobreak >nul
)

echo.
echo 🌐 Opening extension interfaces...
echo.

REM Open WhatsApp checker
start extensions\whatsapp_checker\index.html

REM Open Resume checker
start extensions\resume_checker\index.html

echo.
echo 📋 Instructions:
echo 1. WhatsApp Checker: Copy-paste job messages from WhatsApp
echo 2. Resume Checker: Analyze resume-job fit
echo 3. Chrome Extension: Install from extensions\chrome_extension\
echo.
echo 🔧 For Chrome extension:
echo    - Go to chrome://extensions/
echo    - Enable Developer mode
echo    - Load unpacked: select extensions\chrome_extension\
echo.
echo Happy detecting! 🎯
pause