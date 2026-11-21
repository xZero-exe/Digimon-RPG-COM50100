# MDP finito episódico — Digimon RPG v0.6

## Definición formal

Se usa el MDP finito $M=(S,A,P,R,\gamma)$, $\gamma=0.95$. Los episodios parten en una Aldea Digital y acaban al derrotar a Piedmon o agotar la salud. La simulación tiene un límite adicional de 80 turnos (se registra truncamiento si aplica).

**Estado**: $s=(L,H,E,V,D,P,C)$ con:

- `L`: región (6 valores); `H`: salud propia (1 a 6); `E`: energía (0 a 6).
- `V`: vida del enemigo (0 a 6); `D`: forma evolutiva (0 a 3).
- `P`: disponibilidad de una poción (0 o 1).
- `C`: **intención de ataque cargado del enemigo (0 o 1)**, observable en la interfaz.

El dominio nominal contiene $6	imes6	imes7	imes7	imes4	imes2	imes2+2=28\,226$ estados (incluye estados imposibles y victoria/derrota). Un BFS desde el estado inicial recorre **9.493** estados de juego distintos; `C=1` en 4.368 de esos estados.

**Acciones**: explorar por bosque/caverna desde inicio; avanzar o buscar recursos entre encuentros; atacar normal o especial; defender; usar poción; digievolucionar; **interrumpir** (solo si $C=1$ y hay energía).

**Transiciones**: la distribución $P(s'|s,a)$ viene de `DigitalWorld.transitions`. Se combinan acertar/fallar golpes, daño enemigo, emboscadas y la probabilidad de que un enemigo empiece a preparar un ataque especial. Los eventos utilizan probabilidades explícitas; el entorno no necesita información histórica fuera de $s$ para producir una transición. La intención se anuncia con anterioridad, no mediante información oculta.

**Ataque cargado**: cuando `C=1`, el enemigo hace 2 puntos extra de daño bruto y recibe un aumento de 0,09 en probabilidad de impacto (tope 0,98). Puede interrumpirse: gastar 1 energía, 80 % de éxito; si se acierta, anula el contraataque y causa 1 daño que ignora armadura. Si falla, recibe el posible ataque preparado. Las probabilidades de preparar la próxima habilidad son 0,12 bosque; 0,28 caverna; 0,30 pantano; 0,40 ruinas; 0,52 fortaleza.

**Recompensas**: cada acción de combate tiene coste temporal de -1; infligir daño aporta +3 por unidad; daño sufrido penaliza -4 por PS; ganar un combate no final aporta +8, victoria final +100; derrota añade -80. Interrumpir correctamente añade +3. Las recompensas exploratorias se mantienen respecto a v0.5.

## Métodos

**Value Iteration** calcula $V(s)=\max_a\sum_{s'}P(s'|s,a)[R(s,a,s')+\gamma V(s')]$, sin bibliotecas RL. **Control Monte Carlo de primera visita** estima $Q(s,a)$ promediando retornos completos de episodios observados, con política de comportamiento $\epsilon$-greedy, sin consultar el modelo para valorar acciones. Ambos comparten el simulador.

La serialización de políticas es v3 y contiene el séptimo atributo; no admite interpretar políticas v0.5 con estados de v0.6.

## Evaluación base

MC: 40.000 episodios, semilla 42, $\epsilon=0.15$; test: 500 aventuras por política, semilla 2042. Value Iteration tuvo un 84,0 % de victorias y Monte Carlo un 77,2 %. Para el informe final se recomienda repetir con múltiples semillas y comparar la distribución, no una sola muestra.
