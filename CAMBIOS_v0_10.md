# v0.10 — Laboratorio de políticas y explicabilidad

- Nueva clase `PolicyInspector` sin dependencia gráfica: consulta sólo lectura.
- Pantalla `T`: compara la acción recomendada por DP y MC y muestra `Q*(s,a)`, `Q_MC(s,a)` y las visitas MC por cada acción legal.
- Valores DP calculados con Bellman sobre `V*` y modelo MDP original.
- Valores MC medidos de first-visit real en 60.000 episodios, semilla 42, ε=0.15, γ=0.95; nunca se interpreta como estimación un par sin visitas.
- Se confirmó la **igualdad exacta** entre ambas políticas reconstruidas y las guardadas en la v0.9; no se sustituyeron los algoritmos.
- Historial interactivo para revisar decisiones de turnos anteriores sin alterar el MDP ni el episodio.
- Integridad del análisis asociada mediante SHA-256 a `dp.json` y `mc.json`; falla segura ante desajuste.
- Nueva herramienta sin Pygame: `python -m digimon_rl.inspect_policies [--csv ruta.csv]`.
- El arte Digidex aportado por el usuario se conserva solo para pruebas locales. No publicar sin los permisos correspondientes.
- La ventana SDL/Pygame no se ha verificado en Windows; pruebas automatizadas de control e inspector disponibles sin Pygame.
