# Cambios v0.6 — Combate táctico y exploración en mapa

1. Se incorporó el estado observable `enemy_charging` (bool) al `GameState`.
2. Ataques cargados de cinco enemigos: probabilidades por región (`DigitalWorld.CHARGE_PROB`), mayor daño y precisión, anunciado antes del siguiente turno.
3. Nueva acción `Action.INTERRUPT` que consume energía, puede anular el golpe anunciado y hace un punto de daño al acertar. `Action.GUARD` absorbe mejor los golpes fuertes.
4. El selector inicial de rutas permite hacer clic en los nodos del mapa en modo manual. No es movimiento libre por una cuadrícula.
5. Se incorporaron señales visuales y el nombre del ataque cargado enemigo. La pantalla de ayuda y el registro describen estas interacciones.
6. `policy_io` pasa a formato 3 para distinguir claramente las políticas y estados de la versión anterior.
7. Espacio nominal: 28.226; estados alcanzables: 9.493. Programación Dinámica y Monte Carlo reentrenadas.
8. Se añadieron 7 pruebas específicas de intención enemiga, para **50 pruebas automatizadas aprobadas**.
9. Evaluación de 500 aventuras: DP 420 victorias (84,0 %); MC 386 (77,2 %). Entrenamiento MC 40.000 episodios.

Ver `README.md`, `docs/modelo_mdp_v0_6.md`, `resultados/validacion_v0_6.json` y gráficos.

## Notas de compatibilidad

- Las políticas v0.5 deben sustituirse por las v0.6; no reutilizarlas porque el estado tiene ahora 7 componentes.
- La interfaz aún representa el mapa como grafo de regiones, no como exploración libre de personaje en cada píxel; esto evita añadir posiciones cosméticas al MDP.
- Los sprites de Digidex están incluidos solo para el uso local acordado con el usuario, con las advertencias en `AVISO_DERECHOS_SPRITES.md`.
