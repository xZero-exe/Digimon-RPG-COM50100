# Versión 0.8.1 — Corrección del instalador Windows

La lógica del MDP, el combate, los sprites y las políticas v0.8 no cambian.

## Error detectado

Al ejecutar `JUGAR_WINDOWS.bat` directamente desde la vista de un ZIP en el Explorador, Windows lo coloca en una ruta temporal y **no extrae necesariamente** el archivo `pyproject.toml`. Por ello `pip install -e ".[game]"` falla con `neither setup.py nor pyproject.toml found`.

## Correcciones

- `JUGAR_WINDOWS.bat` **comprueba primero** si existen `pyproject.toml`, el código `src` y las políticas; si faltan, explica cómo extraer el ZIP y muestra la carpeta actual, sin invocar a pip.
- Crea el entorno virtual `.venv` para usar dependencias aisladas en cada computador.
- Comprueba Python 3.11+ con `py -3` y `python` como respaldo.
- Instalación inicial de Pygame y del proyecto solo cuando se necesitan.
- Ejecución del juego mediante el Python de `.venv`, con rutas relativas explícitas `--policies` y `--assets`.
- Mensajes de error separados para extracción, Python, entorno virtual, pip y juego.
- Instrucciones de instalación actualizadas en README y documento de inicio incluido al comienzo del ZIP.

## Forma correcta de ejecución

1. Descomprimir **todo** el ZIP con «Extraer todo».
2. Abrir la carpeta `digimon_rpg_rl` que contiene `pyproject.toml`.
3. Ejecutar `JUGAR_WINDOWS.bat` allí. La primera instalación requiere conexión a Internet.

**El archivo `.bat` no puede iniciar un juego que no se extrajo: esa situación se detecta y explica, en lugar de fallar silenciosamente.**
