# v0.12 — Panel académico y presentación en Pygame

## Alcance

La versión se enfoca en **presentación y evaluación reproducible**. Se mantienen las políticas, reglas del MDP v0.9, técnicas especiales, rutas RPG y sprites locales de v0.11.

- `F4`: panel de cuatro métricas, alimentado por `resultados/convergencia_v011/curvas_resumen.csv` y `resumen_v011.json`; no hay datos de demostración inventados.
- `F5`: seis diapositivas narrativas con contenido académico, datos reales y acceso al juego con agentes entrenados.
- `T`: laboratorio de políticas de v0.10, sin cambios.
- `src/digimon_rl/academic_dashboard.py`: clase independiente de Pygame, validaciones CSV y JSON, fórmulas de métricas y guion.
- `src/digimon_rl/presentation.py`: nuevos estados de navegación `RESULTS` y `DEMO`.
- `src/digimon_rl/gui/app.py`: gráficos dibujados con primitivas Pygame; interfaz de lectura, sin bibliotecas de gráficos ni entrenamiento en render.
- `tests/test_academic_dashboard_v012.py`: diez pruebas nuevas sobre métricas, CSV, parámetros, navegación y preservación de partida.

## Validación

- 114/114 pruebas `unittest` aprobadas.
- Auditor de dependencias: cero librerías conocidas de aprendizaje reforzado detectadas en 49 archivos Python.
- No se cambiaron `agents.py`, `environment.py` ni las políticas persistidas en `politicas/`.
- **Pendiente:** ejecutar la pantalla real de Pygame en un equipo Windows (el entorno de construcción carece de Pygame y de acceso de red para instalarlo).

## Restricciones académicas

- Programación Dinámica: `ValueIterationAgent` implementado desde cero (NumPy solo como álgebra numérica).
- Monte Carlo: control on-policy First-Visit ε-greedy implementado desde cero conforme a la Cátedra 13.
- No se utilizan paquetes especializados de RL.
- El experimento mostrado en el panel es **v0.11**: checkpoints entre 500 y 20.000 episodios, cinco semillas, 200 partidas de evaluación por método/semilla/checkpoint. La política de juego MC guardada corresponde a **60.000 episodios**; no mezclar ambas cifras.

## Derechos de imágenes

Los sprites de Digidex son aportados por el usuario para pruebas locales, no deben subirse al GitHub público sin permiso expreso de los artistas.
