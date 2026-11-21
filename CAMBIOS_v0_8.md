# Cambios v0.8 — Progresión RPG y entrenamiento

## Funciones nuevas

- Cada combate ganado fuera de la fortaleza concede **1 XP**, hasta un máximo de **2 XP** acumulables.
- Al terminar un combate, si hay **2 XP**, al menos **1 energía** y todavía no se entrenó, la acción voluntaria **Mejorar ataque** está disponible.
- Entrenar consume **2 XP**, **1 energía** y un turno; recompensa inmediata **−3**. A cambio, aumenta en **+1 el daño** de ataques normales y especiales durante el resto de la aventura.
- La mejora es **permanente durante un episodio**, incluso al avanzar de región, y solo puede comprarse una vez por aventura.
- Se muestran `XP 0/2`, `XP 1/2` o `XP 2/2` y `ATAQUE +0/+1` en el HUD de combate, y se anuncian los eventos de entrenamiento y las recompensas de experiencia.
- Se agregó prueba automatizada de persistencia de progresión, restricciones de recursos, daño aumentado, elección voluntaria, serialización y compatibilidad de políticas.

## MDP

El estado ahora tiene **10 variables**: `(zone, hp, energy, enemy_hp, evolved, potion, enemy_charging, data_core, xp, trained)`.

- `xp`: entero en {0, 1, 2}.
- `trained`: bool, indicador de una mejora ya aplicada.
- `TRAIN`: acción legal únicamente en una región despejada, con XP ≥2, energía ≥1 y sin entrenamiento previo.
- La función de transición continua siendo la única fuente de reglas, compartida por DP y MC; el modo gráfico solo representa el estado.
- Espacio nominal: **395.138** combinaciones incluyendo dos terminales.
- Estados alcanzables: **48.553** no terminales desde el inicio.

**Validación completa: 64 pruebas automatizadas aprobadas**. Value Iteration convergió en 34 iteraciones (42,56 s), Monte Carlo se entrenó durante 90.000 episodios (55,36 s). En 500 episodios de evaluación: Value Iteration 468 victorias (93,6 %) y Monte Carlo 437 (87,4 %).

Se modificó la serialización a **formato de política v5**; las políticas anteriores se rechazan explícitamente.

## Compatibilidad, pruebas y limitaciones

- Se conservan la selección de rutas, el núcleo, los encuentros anunciados y las 4 etapas Agumon → Greymon → MetalGreymon → WarGreymon.
- Continúan disponibles **Value Iteration** y **control Monte Carlo first-visit ε-greedy**, implementados sin librerías de RL.
- Para la entrega académica final es necesario evaluar varias semillas y controlar el sesgo introducido por los estados no visitados por MC.
- La interfaz gráfica Pygame necesita prueba de apertura en Windows; las pruebas automáticas sin SDL no sustituyen una verificación visual.
- Los sprites de Digidex adjuntados por el usuario siguen dentro de esta *edición local*. No se deben incluir en repositorio GitHub público sin permiso de sus autores.
