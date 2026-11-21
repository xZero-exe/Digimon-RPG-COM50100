# Cambios v0.7 — Rutas del Mundo Digital

- Se incorporó la región Torre de Datos como ruta alternativa a Ruinas Antiguas.
- Se añadió Andromon, su sprite pixel art proporcionado por el usuario y un fondo local nuevo.
- Se agregó `data_core: bool` al estado observable, con probabilidad de hallazgo en exploración, bonificación en el jefe final y registro en el HUD.
- El nuevo campo forma parte de la función de transición: MDP de ocho componentes, persistencia de políticas **formato 4**.
- El mapa utiliza `visited_zones` para reflejar el camino realmente realizado.
- Se reentrenaron ambas políticas: DP 21.337 estados, Monte Carlo 60.000 episodios (10.513 estados visitados con acción aprendida).
- Evaluación (500 aventuras): DP 87,4 % y MC 80,6 %. Ver `resultados/validacion_v0_7.json`.
- Total de **56 pruebas automatizadas** aprobadas, incluidas seis nuevas de exploración y núcleo.

## Compatibilidad
No utilizar políticas antiguas con el MDP nuevo. Para conservar reproducibilidad y evitar acciones no válidas, la carga rechaza versiones distintas de v4.

## Limitaciones
Este prototipo mantiene exploración como elecciones discretas de ruta, no desplazamiento libre en un mapa de baldosas. La visualización en Pygame debe probarse en un computador con esa biblioteca instalada. Arte de terceros solo para pruebas locales sujetas a permisos.
