# v0.9 – Habilidades exclusivas y cálculo DP optimizado

- Nueva `Action.TECHNIQUE` con `Technique` como objeto de dominio inmutable.
- Agumon: Baby Flame; Greymon: Mega Flame; MetalGreymon: Giga Destroyer; WarGreymon: Terra Force.
- Costos, acierto, daño, perforación de armadura e interrupción calculados en una única transición MDP.
- Misma definición de estado y mismo número de estados alcanzables que v0.8.2.
- Value Iteration usa vectorización NumPy; **misma ecuación de Bellman y misma política objetivo**, sin librerías RL.
- Monte Carlo permanece **on-policy First-Visit ε-greedy** (Cátedra 13), con rechazo de episodios truncados.
- Nuevas políticas guardadas en formato 6; no son compatibles las antiguas por cambio de reglas.
- Juego manual: nueva opción por forma, HUD informativo y efecto de técnica.
- 83 pruebas automatizadas aprobadas. La validación visual Pygame queda pendiente de Windows.
- Evaluación principal (500 partidas por método, semilla 2042): DP 94,2 %, MC 90,6 %; MC entrenado 60.000 episodios y 2 acciones de respaldo registradas.
- No redistribuir sprites de Digidex públicamente sin autorización de autores.
