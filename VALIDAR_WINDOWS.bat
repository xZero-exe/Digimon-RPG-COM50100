@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "PYTHONPATH=%~dp0src"
title Digimon RPG v0.22 - Validacion Windows
if not exist "src\digimon_rl\play.py" goto FALTA_PROYECTO
if not exist ".venv\Scripts\python.exe" goto FALTA_ENTORNO
if not exist "resultados\validacion_windows" mkdir "resultados\validacion_windows"
echo [1/16] Comprobando dependencias de aprendizaje reforzado...
".venv\Scripts\python.exe" scripts\verificar_sin_librerias_rl.py > "resultados\validacion_windows\auditoria.txt" 2>&1
if errorlevel 1 goto ERROR_VALIDACION
echo [2/16] Ejecutando pruebas automatizadas...
".venv\Scripts\python.exe" -m unittest discover -s tests -v > "resultados\validacion_windows\pruebas.txt" 2>&1
if errorlevel 1 goto ERROR_VALIDACION
echo [3/16] Probando pantallas SDL, resoluciones y agentes...
echo Se abriran ventanas brevemente. Espera hasta que terminen.
".venv\Scripts\python.exe" scripts\validar_interfaz_v013.py --output "resultados\validacion_windows\interfaz" > "resultados\validacion_windows\interfaz.txt" 2>&1
if errorlevel 1 goto ERROR_VALIDACION
echo.
echo [4/16] Validando los diez efectos y la galeria F6...
".venv\Scripts\python.exe" scripts\validar_efectos_v014.py --output "resultados\validacion_windows\efectos" > "resultados\validacion_windows\efectos.txt" 2>&1
if errorlevel 1 goto ERROR_VALIDACION
echo [5/16] Validando ataques basicos en las cuatro formas...
".venv\Scripts\python.exe" scripts\validar_basicos_v0141.py --output "resultados\validacion_windows\basicos" > "resultados\validacion_windows\basicos.txt" 2>&1
if errorlevel 1 goto ERROR_VALIDACION
echo [6/16] Validando los nueve fondos y sus encuadres...
".venv\Scripts\python.exe" scripts\validar_fondos_v015.py --output "resultados\validacion_windows\fondos" > "resultados\validacion_windows\fondos.txt" 2>&1
if errorlevel 1 goto ERROR_VALIDACION
echo [7/16] Validando mensajes, barras y controles de combate...
".venv\Scripts\python.exe" scripts\validar_combate_v016.py --output "resultados\validacion_windows\combate" > "resultados\validacion_windows\combate.txt" 2>&1
if errorlevel 1 goto ERROR_VALIDACION
echo [8/16] Validando mapa ilustrado, rutas y clics...
".venv\Scripts\python.exe" scripts\validar_mapa_v017.py --output "resultados\validacion_windows\mapa" > "resultados\validacion_windows\mapa.txt" 2>&1
if errorlevel 1 goto ERROR_VALIDACION
echo [9/16] Validando sonido, preferencias y transiciones...
".venv\Scripts\python.exe" scripts\validar_audio_v018.py --output "resultados\validacion_windows\audio" > "resultados\validacion_windows\audio.txt" 2>&1
if errorlevel 1 goto ERROR_VALIDACION
echo [10/16] Comprobando informe historico v0.19...
".venv\Scripts\python.exe" scripts\verificar_entrega_v019.py --output "resultados\validacion_windows\entrega.json" > "resultados\validacion_windows\entrega.txt" 2>&1
if errorlevel 1 goto ERROR_VALIDACION
echo [11/16] Validando evidencia historica de v0.20...
".venv\Scripts\python.exe" scripts\validar_balance_v020.py --output "resultados\validacion_windows\balance_v020.json" > "resultados\validacion_windows\balance_v020.txt" 2>&1
if errorlevel 1 goto ERROR_VALIDACION
echo [12/16] Comprobando un combate real contra Piedmon...
".venv\Scripts\python.exe" scripts\validar_jefe_v021.py --output "resultados\validacion_windows\jefe_v020" > "resultados\validacion_windows\jefe_v020.txt" 2>&1
if errorlevel 1 goto ERROR_VALIDACION
echo [13/16] Validando politicas y curvas del MDP v0.21...
".venv\Scripts\python.exe" scripts\validar_balance_v021.py --output "resultados\validacion_windows\balance_v021.json" > "resultados\validacion_windows\balance_v021.txt" 2>&1
if errorlevel 1 goto ERROR_VALIDACION
echo [14/16] Probando los dos desvios y su botin...
".venv\Scripts\python.exe" scripts\validar_rutas_v021.py --output "resultados\validacion_windows\rutas_v021" > "resultados\validacion_windows\rutas_v021.txt" 2>&1
if errorlevel 1 goto ERROR_VALIDACION
echo [15/16] Probando Digidex, diario y decisiones clave...
".venv\Scripts\python.exe" scripts\validar_digidex_resumen_v022.py --output "resultados\validacion_windows\diario_v022" > "resultados\validacion_windows\diario_v022.txt" 2>&1
if errorlevel 1 goto ERROR_VALIDACION

echo [16/16] Comprobando continuidad del MDP y politicas...
".venv\Scripts\python.exe" scripts\verificar_continuidad_v022.py > "resultados\validacion_windows\continuidad_v022.txt" 2>&1
if errorlevel 1 goto ERROR_VALIDACION

echo VALIDACION AUTOMATICA APROBADA EN ESTE EQUIPO.
echo Evidencia: resultados\validacion_windows
echo Revisa tambien la lista visual en docs\digidex_diario_v022.md
pause
exit /b 0
:FALTA_PROYECTO
echo Extrae todo el ZIP antes de ejecutar este archivo.
pause
exit /b 2
:FALTA_ENTORNO
echo Ejecuta primero JUGAR_WINDOWS.bat para preparar el entorno.
echo Cierra el juego y vuelve a ejecutar VALIDAR_WINDOWS.bat.
pause
exit /b 3
:ERROR_VALIDACION
echo Alguna comprobacion fallo. Conserva los registros completos.
echo Revisa los archivos de resultados\validacion_windows.
pause
exit /b 1
