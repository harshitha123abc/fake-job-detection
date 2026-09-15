#!/bin/bash

# Direct Access Extensions Launcher
# This script helps you quickly test all the direct access interfaces

echo "🚀 Fake Job Detection - Direct Access Extensions"
echo "================================================"
echo ""

# Check if API is running
echo "📡 Checking if Flask API is running..."
if curl -s http://localhost:5000/health > /dev/null; then
    echo "✅ API is running on http://localhost:5000"
else
    echo "❌ API is not running. Please start it with: python api.py"
    echo ""
    echo "Starting API..."
    python api.py &
    sleep 3
fi

echo ""
echo "🌐 Opening extension interfaces..."
echo ""

# Open WhatsApp checker
if command -v xdg-open > /dev/null; then
    xdg-open "extensions/whatsapp_checker/index.html"
elif command -v open > /dev/null; then
    open "extensions/whatsapp_checker/index.html"
else
    echo "📱 WhatsApp Checker: file://$(pwd)/extensions/whatsapp_checker/index.html"
fi

# Open Resume checker
if command -v xdg-open > /dev/null; then
    xdg-open "extensions/resume_checker/index.html"
elif command -v open > /dev/null; then
    open "extensions/resume_checker/index.html"
else
    echo "📄 Resume Checker: file://$(pwd)/extensions/resume_checker/index.html"
fi

echo ""
echo "📋 Instructions:"
echo "1. WhatsApp Checker: Copy-paste job messages from WhatsApp"
echo "2. Resume Checker: Analyze resume-job fit"
echo "3. Chrome Extension: Install from extensions/chrome_extension/"
echo ""
echo "🔧 For Chrome extension:"
echo "   - Go to chrome://extensions/"
echo "   - Enable Developer mode"
echo "   - Load unpacked: select extensions/chrome_extension/"
echo ""
echo "Happy detecting! 🎯"