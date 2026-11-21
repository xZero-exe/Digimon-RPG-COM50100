# Guion sugerido para presentar Digimon RPG en 10 minutos — v0.12

## Objetivo de la demostración

Mostrar un MDP finito y episódico en un RPG, con dos algoritmos escritos manualmente: Value Iteration y control Monte Carlo First-Visit on-policy con ε-greedy, de acuerdo con la Cátedra 13.

| Minutos | Pantalla / tecla | Guion |
|---|---|---|
| 0:00–1:00 | Menú / `F5`, diapositiva 1 | Objetivo y por qué Digimon RPG permite decisiones secuenciales. |
| 1:00–2:30 | F5, diapositiva 2 | Las 10 variables del estado, acciones legales, transiciones, recompensas y condiciones de término. |
| 2:30–4:00 | F5, diapositiva 3 | Value Iteration conoce P(s'|s,a); Monte Carlo aprende a partir de episodios completos, sin usar el modelo para estimar Q. |
| 4:00–5:30 | F5, diapositiva 4 | Gráfico de victorias: media de 5 semillas, desde 14,9 % (500 ep.) hasta 82,6 % (20.000 ep.), frente a 96 % de DP. |
| 5:30–6:30 | F5, diapositiva 5 | Cobertura, respaldos, aleatoriedad y limitaciones: no confundir aprendizaje observado con prueba de convergencia. |
| 6:30–8:30 | F5, diapositiva 6 → `F1` o `F2` | Mostrar una aventura: escoger ruta, combatir, decidir recursos y digievolucionar. |
| 8:30–9:30 | Juego → `T` | Inspeccionar política en un estado: acción recomendada y Q(s,a), sin inventar valores no aprendidos. |
| 9:30–10:00 | Juego → `F4` | Recordar conclusión, limitaciones y fuentes del curso. |

## Controles

- `F4` desde inicio o partida: panel de resultados. Flechas izquierda/derecha para seleccionar métricas; `Esc` para volver.
- `F5`: presentación guiada. `Espacio` o derecha avanza, izquierda retrocede; `F1/F2` inicia el juego desde cualquier diapositiva; `Esc` vuelve.
- Durante el juego: `T` muestra laboratorio de valores Q; `A` reproduce automáticamente, `Espacio` avanza un paso, `R` reinicia.

## Qué datos se muestran exactamente

El panel utiliza el **experimento v0.11**: cinco semillas de entrenamiento MC (41 a 45), evaluaciones de 200 episodios por semilla y checkpoint, γ=0,95 y ε=0,15. La desviación estándar mostrada es **entre semillas**, no un intervalo de confianza. No se está evaluando la política MC guardada de 60.000 episodios cuando se ve la curva de 20.000. Las dos políticas guardadas para jugar provienen del MDP v0.9.

## Defensa académica

La comparación es coherente porque los dos agentes juegan el mismo entorno; no implica que el rendimiento en una muestra sea idéntico en todas las semillas. La cobertura registra estados con al menos una acción aprendida y las acciones de respaldo reconocen las regiones poco visitadas. El curso permite las implementaciones descritas en sus cátedras; NumPy y Pygame no realizan aprendizaje reforzado.

Referencias: Pastene (2026), Cátedra 13; Sutton y Barto (2018), capítulo 5; Bertsekas (2017).

**Créditos:** reconocer a Digidex y a sus artistas; mostrar `CREDITOS.md` y la pantalla C del juego.
