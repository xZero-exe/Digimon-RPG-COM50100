# v0.13 — Interfaz adaptable y preparación del informe

Base: v0.12 Panel Académico y Modo Demostración. Se conserva el proyecto completo, sus sprites, políticas, experimentos y funciones anteriores.

- Ventana redimensionable, tamaño inicial ajustado al escritorio, proporción constante con bandas y transformación de coordenadas para los clics.
- F11 entra o sale de pantalla completa; conserva el tamaño anterior de ventana.
- Dos filas de acciones manuales cuando hay más de cuatro; etiquetas ajustadas por ancho y ayudas al pasar el ratón.
- F4 y F5 también son botones en la cabecera del juego.
- Separación de energía, XP y valores de salud enemiga; bienvenida fuera de la figura del protagonista.
- Eje X de los gráficos proporcional al número real de episodios, en lugar de distancias iguales entre puntos de control.
- `scripts/validar_interfaz_v013.py`: render real de Pygame, 24 capturas, navegación, resoluciones, clics, formas, finales y aventuras completas.
- `VALIDAR_WINDOWS.bat`: pruebas, auditoría y diagnóstico gráfico con registros del SO real.
- Informe preliminar DOCX y Markdown con las nueve secciones exigidas, más guía de cierre y aceptación en Windows.

## Validación

La evidencia incluida identifica Linux y SDL dummy. No certifica ejecución nativa en Windows; esa aceptación queda pendiente y dispone de un procedimiento concreto. Consultar `docs/validacion_windows_v013.md`, `resultados/pruebas_v013.txt` y `resultados/interfaz_v013/validacion.json`.

Los cambios se limitan a presentación, distribución y documentación; no agregan algoritmos RL. Se mantienen Value Iteration y Monte Carlo on-policy First-Visit ε-greedy programados manualmente, y la arquitectura POO.
