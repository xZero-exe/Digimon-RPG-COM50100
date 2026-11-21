# Notas de versión — v0.2

## Incorporado

- `AdventureController`: lógica de sesión independiente de Pygame, con modos DP, MC y manual.
- `RPGApp`: mapa de seis regiones, escena de combate, arte geométrico provisional, barras de salud y energía, botones, log y pantalla final.
- Reproducción paso a paso, automática con control de velocidad, reinicio y acciones manuales.
- Serialización y carga validada de políticas en JSON (`policy_io.py`).
- Comando `python -m digimon_rl.train` para generar políticas y `python -m digimon_rl.play` para abrir la interfaz.
- Políticas preentrenadas incluidas en `politicas/` (DP 1537 estados, MC 962 estados aprendidos en 10.000 episodios).
- Ocho pruebas adicionales para persistencia y controlador, total 16.
- Dependencia Pygame opcional (`pip install -e ".[game]"`).

## Conservado

- MDP original (2306 estados nominales, 1537 alcanzables, 2 terminales).
- Value Iteration y first-visit on-policy Monte Carlo sin frameworks de RL.
- Ejecutable de consola, salida de CSV/JSON, gráficos opcionales, pruebas previas.

## Validado y por verificar

- **Validado aquí:** sintaxis de todos los módulos, tests `unittest` 16/16, exportación/importación de políticas, simulación y evaluación de 500 episodios por método, detección de ausencia de Pygame.
- **Pendiente de comprobación local:** visualización y eventos de ventana Pygame (la dependencia no se pudo instalar en el entorno de generación).

## Próximos hitos sugeridos

1. Probar interfaz en Windows y capturar incidencias de distribución visual o controles.
2. Ajustar el balance del MDP para que existan decisiones difíciles y evitar políticas triviales.
3. Incorporar arte original más detallado y animaciones, preservando el modelo matemático.
4. Experimentar con múltiples semillas, curvas de aprendizaje y análisis estadístico.
