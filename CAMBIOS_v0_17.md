# v0.17 — Mapa ilustrado del Mundo Digital

- Paisaje nuevo de pixel art con las siete regiones y sus ocho conexiones reales.
- Posición y forma actuales, recorrido dorado, regiones despejadas y rutas disponibles.
- Destinos manuales pulsables únicamente cuando sus acciones son legales.
- Seguimiento de DP/MC sin intervención del mapa sobre sus decisiones.
- Avisos narrativos en el registro, con texto distribuido en líneas y mapa despejado.
- Protección ante clics repetidos sobre acciones que dejaron de ser legales.
- Respaldo esquemático si falta la imagen y diagnóstico con cuatro resoluciones.
- Octavo paso de `VALIDAR_WINDOWS.bat`.
- 152/152 pruebas aprobadas, ocho rutas verificadas y 44 capturas nuevas.

Se conservan el MDP, las políticas, los algoritmos manuales y las funciones de v0.16.
Guía: `docs/mapa_v017.md`. Evidencia: `resultados/mapa_v017/`.
La validación nativa en Windows requiere ejecutar el BAT en ese sistema.
