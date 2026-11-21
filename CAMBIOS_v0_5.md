# v0.5 — Digievolución avanzada

- Se amplían las formas de Agumon: **Agumon → Greymon → MetalGreymon → WarGreymon**.
- Cada evolución exige energía y regiones habilitadas; se activa mediante la acción `DIGIVOLVE`, nunca automáticamente.
- WarGreymon requiere llegar a la Fortaleza Virus como MetalGreymon y disponer de 3 de energía.
- Las formas más avanzadas aumentan daño y resistencia; Piedmon tiene 6 PS, armadura viral y ataques fuertes.
- El MDP pasa a **14.114 estados nominales** (incluidos victoria y derrota) y **4.705 estados no terminales alcanzables**.
- Las políticas JSON anteriores **no son compatibles**: formato actualizado a v2 y políticas entrenadas otra vez.
- Dos sprites x5 adicionales del ZIP Digidex entregado por el usuario; **solo para uso local**, no subir a GitHub sin permiso de sus artistas.
- Se conservan la arquitectura POO, Programación Dinámica, Monte Carlo y las mismas 6 regiones.
- Las reglas y probabilidades se comparten mediante `DigitalWorld.transitions`, no hay simulador alternativo.

## Balance deliberado

No siempre conviene digievolucionar. El coste es un turno de combate y energía; la transformación a Mega aporta protección temporal y daño suficiente para superar con mayor eficacia la armadura de Piedmon.

## Restricciones y validación

No se pudo probar visualmente Pygame en este entorno; sí se realizaron pruebas automatizadas de lógica y empaquetado. Para el informe, medir recursos y tiempos en el PC del estudiante, repetir las evaluaciones con varias semillas y no comparar un modelo viejo contra políticas nuevas.
