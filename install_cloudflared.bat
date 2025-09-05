
@echo off
echo Installing Cloudflared for Windows...

REM Check if already installed
where cloudflared >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Cloudflared already installed
    cloudflared --version
    goto :end
)

echo Downloading cloudflared...
curl -L --output cloudflared.exe https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe

if %ERRORLEVEL% EQU 0 (
    echo Moving to PATH...
    move cloudflared.exe %WINDIR%\System32\
    echo Cloudflared installed successfully!
    cloudflared --version
) else (
    echo Failed to download cloudflared
    exit /b 1
)

:end
pause
