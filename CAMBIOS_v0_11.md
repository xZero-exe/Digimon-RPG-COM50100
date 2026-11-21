# v0.11 — Curvas de aprendizaje y auditoría académica

- El proyecto **no incorpora bibliotecas de aprendizaje reforzado**. La implementación de Value Iteration y Monte Carlo On-policy First-Visit ε-greedy sigue en `src/digimon_rl/agents.py`.
- Nuevo `scripts/verificar_sin_librerias_rl.py`: comprueba con AST importaciones y dependencias de bibliotecas RL conocidas (Python estándar).
- Nuevo `scripts/curvas_aprendizaje_v011.py`: entrena MC incrementalmente con cinco semillas, evaluando la política greedy en cinco presupuestos acumulativos; usa Value Iteration guardada como comparación.
- Nuevo `tests/test_academic_v011.py`: ocho pruebas para integridad académica, continuidad de entrenamiento, truncamientos y estadísticas.
- Ajuste en `MonteCarloAgent.train`: la numeración de episodios ya no vuelve a 1 al realizar varias llamadas; el aprendizaje no cambia y la continuación es idéntica al entrenamiento continuo.
- Nuevos CSV, JSON y gráficos SVG para análisis y defensa de la presentación.
- Se conservan los sprites de la edición local, las políticas entrenadas del MDP v0.9, las regiones, las digievoluciones y la interfaz v0.10. No se alteran las reglas del juego ni el modelo.
- Restricción: **no publicarse sprites Digidex en GitHub sin la autorización de los artistas.**
- Para Windows: nuevo `VERIFICAR_SIN_RL_WINDOWS.bat`, que ejecuta el auditor sin abrir el videojuego.
