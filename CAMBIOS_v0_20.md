# v0.20 — Balance de Piedmon y WarGreymon

- Piedmon: 9 PS en vez de 6; los demás enemigos mantienen sus parámetros.
- Digievolucionar a WarGreymon: 2 EN en vez de 3, todavía consume un turno.
- Resistencia pasiva de WarGreymon: hasta 2 PS por golpe; MetalGreymon mantiene 1.
- La reducción pasiva nunca vuelve invulnerable al protagonista: mínimo 1 PS.
- Sin evolución forzada ni recompensas por mostrar una forma determinada.
- Políticas DP/MC y valores del laboratorio recalculados para las nuevas reglas.
- Cinco nuevas curvas MC; resultados históricos conservados y distinguidos.
- 60.649 estados no terminales alcanzables y dos terminales; mismas diez variables.
- Ayuda contextual contra Piedmon y validación Windows ampliada a doce pasos.
- Ocho pruebas nuevas de regresión del balance.

Esta etapa equilibra el combate antes de ampliar caminos o enemigos. Conserva
las siete regiones, los seis enemigos y todos los recursos de v0.19. No añade
algoritmos de aprendizaje ni bibliotecas RL. El Word v0.19 es histórico; el anexo
`docs/balance_v020.md` documenta las cifras actuales para la siguiente revisión.
