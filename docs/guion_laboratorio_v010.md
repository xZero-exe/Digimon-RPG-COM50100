# Guion breve de presentación — laboratorio de políticas (v0.10)

1. Abre el juego y presiona **F1** (Value Iteration), luego **T**.
2. En la Aldea Digital, compara rutas: ambas políticas eligen el Bosque. Muestra la columna **Q\* DP** calculada con Bellman y la columna **Q MC**, estimada a partir de retornos observados.
3. Señala que la columna **Visitas MC** muestra el tamaño de la muestra para cada par (estado, acción). Una fila **No visitado** no tiene estimación MC.
4. Regresa y avanza varios turnos. Presiona **T**, luego las flechas para observar estados anteriores sin alterar la partida.
5. Alterna entre F1 y F2 para mostrar la misma interfaz y sus decisiones, recordando que cambiar de modo inicia un nuevo episodio.
6. Explica que DP conoce las probabilidades de transición, mientras que MC aprende episodios simulados. Ambos emplean el mismo MDP; la interfaz no aprende ni altera recompensas.
7. Para reproducir fuera de Pygame: `python -m digimon_rl.inspect_policies --csv resultados/ejemplo_valores_q.csv`.

**Advertencia sobre Q:** los valores DP corresponden al valor óptimo con modelo conocido; los MC son promedios first-visit bajo la política de entrenamiento. Sus diferencias no miden directamente un "error" comparativo sin controlar la política y la distribución de estados.

**Bibliografía principal del curso:** Sutton y Barto (2018), capítulo 4 (DP) y capítulo 5 (Monte Carlo); clases de Programación Dinámica y Cátedra 13 del profesor Matías Pastene (MC on-policy sin exploring starts).
