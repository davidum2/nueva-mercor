@echo off
echo ========================================================
echo Iniciando Comet Browser en modo depuracion (CDP: 9223)
echo ========================================================
set COMET_PATH=%LOCALAPPDATA%\Perplexity\Comet\Application\comet.exe

if not exist "%COMET_PATH%" (
    echo [ERROR] No se encontro comet.exe en: "%COMET_PATH%"
    pause
    exit /b 1
)

start "" "%COMET_PATH%" --remote-debugging-port=9223
echo Comet lanzado con flag --remote-debugging-port=9223.
