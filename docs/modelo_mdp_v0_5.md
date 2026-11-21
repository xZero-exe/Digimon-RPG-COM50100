# MDP finito episódico — v0.5

Estado `GameState(zone, hp, energy, enemy_hp, evolved, potion)` donde `evolved ∈ {0,1,2,3}` es el **nivel de evolución**. Dos terminales `WIN/LOSS`. `hp∈[1,6]`, `energy∈[0,6]`, `enemy_hp∈[0,6]`, `zone∈{0,1,2,3,4,5}` y `potion∈{0,1}`.

\[|S|=6\cdot 6\cdot 7\cdot 7\cdot 4\cdot 2+2=14114\]

BFS sobre transiciones válidas desde la Aldea Digital da **4705 estados no terminales alcanzables**. El valor puede cambiar si se reequilibran reglas.

La acción `DIGIVOLVE` sube **una etapa** (no se puede saltar de Agumon a WarGreymon). Requiere el nivel, región y energía adecuados. Ataques con probabilidad de acertar y enemigo con probabilidad de golpear generan las transiciones estocásticas.

Recompensas: daño causado `+3` por PS, daño sufrido `-4` por PS, coste temporal del turno `-1`, combate superado `+8`, finalización `+100` y derrota `-80`; exploración `+2` salvo amboscadas con penalización. Se comparan Value Iteration sobre el modelo explícito y Monte Carlo first-visit on-policy con exploración epsilon-greedy.

Un episodio termina con jefe derrotado, caída a 0 PS o truncamiento de seguridad por límite de turnos, contabilizado separadamente al evaluar. Las probabilidades dependen solo de `(estado, acción)`; evolución y recursos no son variables ocultas.
