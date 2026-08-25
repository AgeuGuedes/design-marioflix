@echo off
title MarioFlix
cd /d "%~dp0"

echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo Python nao foi encontrado neste computador.
    echo Instale em https://www.python.org/downloads/ e marque a opcao "Add python.exe to PATH" durante a instalacao.
    echo Depois, rode este arquivo de novo.
    pause
    exit /b
)

echo Python encontrado. Instalando dependencias (so demora na primeira vez)...
python -m pip install -r requirements.txt

echo.
echo Iniciando o servidor do MarioFlix...
start "MarioFlix - servidor (nao feche)" cmd /k python -m uvicorn src.api.main:app

timeout /t 4 /nobreak >nul
start "" http://127.0.0.1:8000

echo.
echo O site deve abrir no navegador em alguns segundos.
echo Para PARAR o site, feche a outra janela preta chamada "MarioFlix - servidor".
pause
