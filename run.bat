@echo off
title A2S - Aesthetics to Spaces
cd /d "%~dp0"

echo.
echo  ========================================
echo   A2S - Aesthetics to Spaces
echo  ========================================
echo.

if not exist "node_modules\" (
    echo [1/2] Installing dependencies...
    call npm install
    if errorlevel 1 (
        echo.
        echo Failed to install dependencies. Check Node.js and npm.
        pause
        exit /b 1
    )
    echo.
) else (
    echo Dependencies found. Skipping npm install.
    echo.
)

echo [2/2] Starting dev server...
echo.
echo  Open the URL shown below in your browser (e.g. http://localhost:5173)
echo  Press Ctrl+C to stop the server.
echo.

call npm run dev

pause
