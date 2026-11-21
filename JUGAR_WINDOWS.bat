@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Digimon RPG v0.22 - Iniciador Windows
set "PYTHONPATH=%~dp0src"

if not exist "pyproject.toml" goto FALTA_EXTRAER
if not exist "src\digimon_rl\play.py" goto FALTA_EXTRAER
if not exist "politicas\dp.json" goto FALTA_ARCHIVOS
if not exist "politicas\mc.json" goto FALTA_ARCHIVOS

set "PYTHON_CMD="
where py >nul 2>nul
if not errorlevel 1 (
    py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=py -3"
)
if not defined PYTHON_CMD (
    where python >nul 2>nul
    if not errorlevel 1 (
        python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
        if not errorlevel 1 set "PYTHON_CMD=python"
    )
)
if not defined PYTHON_CMD goto FALTA_PYTHON

if not exist ".venv\Scripts\python.exe" (
    echo.
    echo [Digimon RPG] Preparando entorno Python aislado...
    %PYTHON_CMD% -m venv ".venv"
    if errorlevel 1 goto ERROR_VENV
)

".venv\Scripts\python.exe" -c "import numpy; import pygame; import digimon_rl" >nul 2>nul
if errorlevel 1 (
    echo.
    echo [Digimon RPG] Instalando el juego y Pygame en .venv...
    echo [Digimon RPG] Se requiere Internet para la primera instalacion.
    ".venv\Scripts\python.exe" -m pip install -e ".[game]"
    if errorlevel 1 goto ERROR_PIP
)

echo.
echo [Digimon RPG v0.14] Abriendo el videojuego...
echo.
".venv\Scripts\python.exe" -m digimon_rl.play --policies "politicas" --assets "assets"
if errorlevel 1 goto ERROR_JUEGO
exit /b 0

:FALTA_EXTRAER
echo.
echo ==============================================================
echo  HAY QUE EXTRAER EL ZIP COMPLETO ANTES DE INICIAR EL JUEGO
echo ==============================================================
echo.
echo Este archivo se esta ejecutando sin el proyecto completo.
echo No se encontro pyproject.toml o el codigo src.
echo.
echo SOLUCION:
echo  1. Cierra esta ventana.
echo  2. Haz clic derecho en el archivo ZIP y elige "Extraer todo".
echo  3. Entra en la carpeta extraida digimon_rpg_rl.
echo  4. Comprueba que veas JUGAR_WINDOWS.bat y pyproject.toml.
echo  5. Ejecuta JUGAR_WINDOWS.bat desde esa carpeta extraida.
echo.
echo Carpeta desde donde intentaste ejecutar:
echo %CD%
echo.
pause
exit /b 2

:FALTA_ARCHIVOS
echo.
echo [ERROR] La extraccion del ZIP no esta completa.
echo Faltan politicas\dp.json o politicas\mc.json.
echo Vuelve a extraer TODO el contenido a una carpeta nueva.
echo.
pause
exit /b 3

:FALTA_PYTHON
echo.
echo [ERROR] No se encontro Python 3.11 o superior.
echo Instala Python desde https://www.python.org/downloads/windows/
echo Selecciona "Add Python to PATH" durante la instalacion.
echo Cierra y vuelve a abrir esta ventana despues de instalar.
echo.
pause
exit /b 4

:ERROR_VENV
echo.
echo [ERROR] No se pudo crear .venv.
echo Verifica permisos de escritura, espacio libre y tu instalacion de Python.
echo.
pause
exit /b 5

:ERROR_PIP
echo.
echo [ERROR] Fallo la instalacion de Pygame o del proyecto.
echo Comprueba la conexion a Internet y prueba otra vez.
echo Si vuelve a fallar, copia el mensaje completo de esta ventana.
echo.
pause
exit /b 6

:ERROR_JUEGO
echo.
echo [ERROR] El juego termino con un error.
echo Copia el mensaje de Python mostrado arriba para diagnosticarlo.
echo.
pause
exit /b 7
