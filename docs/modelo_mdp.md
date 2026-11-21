# Especificación inicial del MDP — Versión 0.2 (modelo base preservado de v0.1)

## 1. Formulación

El mundo se define como un **MDP finito**: \(M=(S,A,P,R,\gamma)\).

- **S:** estados `GameState(zone, hp, energy, enemy_hp, evolved, potion)` más dos estados terminales absorbentes: victoria y derrota.
- **A(s):** acciones legalmente disponibles según el estado; no hay acciones ilegales dentro de las políticas.
- **P(s', r | s, a):** función `DigitalWorld.transitions(s, a)`: retorna todos los posibles `(s', r)` y sus probabilidades (que suman 1).
- **R:** recompensa obtenida por cada transición, con función de recompensa explícita en `environment.py`.
- **γ:** factor de descuento 0.95 por defecto.

Todas las cantidades que modifican acciones y recompensas están dentro del estado. Las probabilidades de acierto y respuesta del enemigo dependen de la zona y del tipo de acción, no de historia no observada: **propiedad de Markov**.

## 2. Estados

| Componente | Valores |
|---|---|
| Zona | 0 Aldea, 1 Bosque, 2 Caverna, 3 Pantano, 4 Ruinas, 5 Fortaleza |
| HP | 1..6 |
| Energía | 0..3 |
| HP enemigo | 0..3 |
| Evolución | Agumon, Greymon |
| Poción | Disponible, gastada |
| Terminal | Victoria, derrota |

Total nominal: `6 * 6 * 4 * 4 * 2 * 2 + 2 = 2306`. El cálculo de Programación Dinámica emplea BFS para identificar estados **alcanzables** desde el inicio; hay 1537 estados alcanzables en v0.1, más dos terminales.

El estado con `enemy_hp = 0` fuera de la Aldea representa el final de un combate y permite elegir una acción de exploración. La zona y la evolución permanecen entre encuentros.

## 3. Dinámica y episodios

- Inicio: Aldea, HP 6, energía 2, Agumon y una poción.
- En la Aldea se elige entre Bosque y Caverna; la Caverna otorga energía adicional pero puede generar una emboscada.
- En zonas intermedias se vence un encuentro para poder avanzar o buscar recursos. Avanzar y buscar llevan a la siguiente región, con riesgos distintos.
- El combate por turnos puede errar ataques y recibir contraataques probabilísticos. Las acciones de curación y digievolución consumen recursos.
- El episodio termina al derrotar al jefe de la Fortaleza o al perder la salud.
- Protección operativa: la simulación se trunca al cumplir 80 acciones si surgiera una trayectoria excepcionalmente larga.

Las transiciones se construyen exhaustivamente y se **normalizan** (la suma debe ser 1). La rutina que muestrea resultados usa esa misma distribución, garantizando la consistencia entre planificación y simulación.

## 4. Métodos

### Programación Dinámica: Value Iteration

Actualización de Bellman óptima:

\[
V_{k+1}(s)=\max_{a\in A(s)} \sum_{s',r}p(s',r\mid s,a)\left[r+\gamma V_k(s')\right].
\]

La iteración finaliza al alcanzar un error inferior a `1e-8` o el máximo de iteraciones. La política greedy se extrae a partir de los valores convergidos.

### Monte Carlo: control on-policy first-visit

Al terminar cada episodio, para cada par `(estado, acción)` en su **primera aparición** dentro del episodio, se calcula el retorno:

\[
G_t=R_{t+1}+\gamma R_{t+2}+\gamma^2 R_{t+3}+\cdots
\]

Se actualiza `Q(s,a)` como media incremental de los retornos y se toman acciones bajo una política `epsilon-greedy` durante entrenamiento. Para evaluación se emplea la política determinista greedy derivada de Q.

Monte Carlo no utiliza la función de transición para calcular valores esperados: solo observa muestras del entorno.

## 5. Alcance y límites conocidos

- Es un **modelo reducido inspirado en un RPG**: un personaje, una evolución, una poción como máximo y salud discretizada. No pretende reproducir todas las reglas de Digimon.
- Las probabilidades de acierto, el daño y las recompensas se **definieron para este prototipo** y se deben documentar como supuestos, no como datos oficiales de videojuegos.
- Para comparaciones finales se requieren **múltiples semillas independientes**, intervalos de confianza y curvas de aprendizaje; los resultados del primer experimento son demostrativos, no conclusiones definitivas.
- La representación visual futura debe leer el estado del modelo, sin modificarlo ni guardar variables ocultas que afecten las transiciones.

## 6. Vista Pygame (v0.2)

La interfaz descrita en [`interfaz_v0_2.md`](interfaz_v0_2.md) visualiza directamente `GameState`, `Action`, `Transition` y las políticas de los agentes. No agrega variables ocultas al modelo ni modifica probabilidades o recompensas; la representación matemática se mantiene respecto de v0.1.
