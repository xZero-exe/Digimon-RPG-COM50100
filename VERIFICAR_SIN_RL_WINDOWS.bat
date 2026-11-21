@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Digimon RPG - Auditoria sin librerias RL

echo.
echo ===========================================================
echo   DIGIMON RPG - VERIFICAR ALGORITMOS SIN BIBLIOTECAS RL

echo ===========================================================
echo.

if not exist "scripts\verificar_sin_librerias_rl.py" (
  echo ERROR: faltan archivos del proyecto. Extrae el ZIP completo primero.
  pause
  exit /b 1
)

if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" "scripts\verificar_sin_librerias_rl.py"
) else (
  where py >nul 2>nul
  if errorlevel 1 (
    echo ERROR: Python no esta disponible. Instala Python 3.11+.
    pause
    exit /b 1
  )
  py -3 "scripts\verificar_sin_librerias_rl.py"
)

if errorlevel 1 (
  echo.
  echo Resultado: ERROR. Revisa las importaciones detectadas.
  pause
  exit /b 1
)

echo.
echo Resultado: OK. Recuerda que la auditoria estatica no sustituye la revision del codigo.
pause
exit /b 0
