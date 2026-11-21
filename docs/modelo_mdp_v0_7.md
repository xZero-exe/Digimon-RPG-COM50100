# Formulación del MDP: Digimon RPG v0.7

## Estado y cardinalidad

`(zona, salud, energía, PS_enemigo, evolución, poción, ataque_cargado, núcleo)`.

7 regiones × 6 niveles de salud (1–6) × 7 energías (0–6) × 7 niveles PS enemigo (0–6) × 4 evoluciones × 2 pociones × 2 indicadores de ataque cargado × 2 valores de núcleo = **65.856 combinaciones nominales**, más `WIN` y `LOSS` = **65.858**. Solo **21.337 estados no terminales** son alcanzables desde `DigitalWorld.start_state()`.

## Exploración

Ruta inicial: Bosque o Caverna. Ambas convergen en Pantano. Desde Pantano puede elegir Ruinas Antiguas o Torre de Datos, que a su vez convergen en Fortaleza Virus. La opción `SCAVENGE` expone a una emboscada (30 %) y puede dar suministros; en Pantano, Ruinas o Torre puede encontrar un núcleo (35 % sobre la búsqueda, si no tiene uno). La elección directa de Torre tiene 37 % de emboscada y 45 % de hallar núcleo, además de poder otorgar +2 de energía.

El núcleo es persistente, visible en el estado, y modifica tanto el daño causado como la armadura de Piedmon. La ruta segura tiene menor riesgo de emboscada (10 % al avanzar). Estas diferencias crean alternativas con recompensas inmediatas frente a beneficio final.

## Combate, evoluciones y transiciones

El daño depende de etapa evolutiva, energía y probabilidades de golpe. Los enemigos preparan ataques según la región; `enemy_charging` indica esta intención antes de la acción del agente. Defender e interrumpir son decisiones tácticas. La clase `DigitalWorld` calcula los resultados probabilísticos y devuelve una distribución normalizada (suma igual a 1).

## Algoritmos

- **Value Iteration** usa explícitamente el modelo de transición y maximiza el retorno esperado descontado.
- **Control Monte Carlo first-visit** estima valores Q de pares estado-acción a partir de episodios completos muestreados, con exploración ε-greedy y política final greedy.
- Ambos métodos comparten los mismos estados, acciones legales, reglas, recompensas y condiciones terminales; no usan librerías externas de RL.

Parámetros de evaluación inicial: γ = 0,95, ε = 0,15, 60.000 episodios de Monte Carlo, 500 episodios de evaluación por política y semillas fijas. Reportar resultados para múltiples semillas en el informe final.

## Estados terminales

El episodio termina al derrotar al jefe (`WIN`) o cuando la salud del protagonista llega a cero (`LOSS`). El simulador además **trunca** a los 80 pasos y registra truncamiento separado de victoria/derrota. Las rutas siempre avanzan hacia el jefe; no hay ciclos de exploración.
