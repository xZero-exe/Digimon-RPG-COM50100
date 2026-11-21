# v0.14.1 — Corrección de sprites en ataques básicos

Se identificaron y corrigieron tres acciones que todavía usaban líneas geométricas: Atacar, Ataque especial e Interrumpir.

- Tres atlas PNG transparentes nuevos, con cuatro fotogramas cada uno.
- Las cuatro digievoluciones utilizan los nuevos sprites para sus acciones generales.
- Galería F6 ampliada a 13 efectos, sin solapamiento entre botones.
- Diagnóstico de cobertura, carga y renderizado de los ataques básicos en las cuatro formas.
- Se conservan los diez atlas anteriores y todas las reglas y políticas.

Detalle: `docs/correccion_ataques_basicos_v0141.md`.

Validación de esta corrección: **135/135 pruebas aprobadas** y diagnóstico de ataques básicos aprobado con Pygame real en Linux/SDL dummy.
