# Digimon RPG — Informe de convergencia y auditoría sin librerías RL (v0.11)

## Objetivo académico

COM50100: comprobar empíricamente cómo evoluciona el control **Monte Carlo on-policy First-Visit, con política de comportamiento ε-greedy** al aumentar los episodios de entrenamiento, y contrastar su desempeño con la política obtenida mediante **Value Iteration**. Ambos algoritmos están desarrollados **manualmente** en `src/digimon_rl/agents.py`, sin Gymnasium, Stable-Baselines, RLlib, ni cualquier otra biblioteca de aprendizaje reforzado. Solo se utilizan NumPy para operaciones de arreglos en Programación Dinámica, Python estándar para Monte Carlo y Pygame para renderizar el RPG.

**Correspondencia con el material:** Cátedra 13, diapositiva 8, *On-policy first-visit MC control (for ε-soft policies)*. Referencia obligatoria: Sutton y Barto (2018), *Reinforcement Learning: An Introduction*, 2.ª edición, cap. 5. Para DP, también Bertsekas (2017). No se han integrado algoritmos de fuera del temario.

## Descripción de la metodología

- **Entorno:** el mismo MDP episódico finito de la versión 0.9, con cuatro digievoluciones y habilidades exclusivas; estado de diez componentes; política DP incluida y generada con γ = 0,95.
- **Método MC:** Q(s,a) estimado exclusivamente desde aventuras muestreadas **completas**, con retorno `G = R + γG` y actualización incremental `Q ← Q + (G−Q)/N`. Se actualiza solo la primera visita del par (s,a) de cada episodio.
- **Comportamiento:** π = ε-greedy respecto a Q, con ε = 0,15; la política para evaluación es greedy y se mantiene congelada durante las evaluaciones.
- **Experimento:** cinco semillas independientes de entrenamiento: 41, 42, 43, 44 y 45. Cada agente MC entrena progresivamente hasta los puntos de control 500, 2000, 5000, 10000 y 20000, **sin reiniciar Q** entre puntos.
- **Evaluación:** 200 episodios por semilla y punto de control, tanto para MC como para DP. Se reutiliza una misma semilla de evaluación por corrida para disminuir variaciones aleatorias, sin afirmar que las trayectorias de políticas distintas sean idénticas. Se registran tasas de victoria, retornos descontados, cobertura de estados y uso de acciones de respaldo.
- **Estadística:** medias y desviación estándar muestral entre semillas; el gráfico muestra promedio ±1 desviación estándar. No es un intervalo de confianza ni una prueba de convergencia teórica.

## Reproducir desde PowerShell, carpeta extraída

```powershell
.\.venv\Scripts\python.exe scripts\verificar_sin_librerias_rl.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts\curvas_aprendizaje_v011.py --seeds 41,42,43,44,45 --checkpoints 500,2000,5000,10000,20000 --eval-episodes 200
```

Si el `.venv` aún no existe, ejecuta antes `JUGAR_WINDOWS.bat` desde la carpeta **extraída**.

### Archivos generados

Se guardan en `resultados/convergencia_v011/`:

- `resultados_por_semilla_y_checkpoint.csv`: datos brutos con todas las corridas, pasos y acciones de respaldo.
- `curvas_resumen.csv`: media y desviación estándar de las métricas principales por punto de control.
- `resumen_v011.json`: parámetros, resultados y limitaciones.
- `convergencia_v011.svg`: curva de victorias MC frente a referencia DP, con dispersión entre semillas.
- `cobertura_v011.svg`: proporción de estados alcanzables visitados por MC.

**Nota sobre DP:** se reutiliza la política precomputada en `politicas/dp.json` para evitar recalcular Value Iteration a cada punto, porque el MDP y γ son idénticos. Este estudio no compara tiempos totales de entrenamiento entre métodos.

## Limitaciones e interpretación

1. La cobertura de estados se define como el porcentaje de estados alcanzables en que al menos un par (s,a) fue actualizado; **no significa** conocer el valor verdadero de cada acción.
2. El aprendizaje no es necesariamente monótono: la política ε-greedy puede explorar y las estimaciones MC se basan en muestras estocásticas.
3. Los episodios truncados por el tope de pasos no actualizan Q: de ese modo no se inventa una recompensa terminal; su conteo se reporta.
4. Al encontrar un estado no visitado, la evaluación ejecuta una acción legal de respaldo y registra cuántas veces ocurrió. Eso puede afectar la tasa de victoria.
5. Las cinco semillas permiten observar variabilidad empírica pero no demuestran convergencia asintótica; para mayor evidencia se pueden utilizar más semillas y entrenar 60.000+ episodios por semilla.
6. La auditoría de dependencias es **estática**, basada en AST: encuentra bibliotecas RL conocidas en importaciones y dependencias declaradas, pero no reemplaza una inspección humana de la ejecución.
7. Los sprites de Digidex incluidos en la edición pública conservan su atribución y procedencia en `CREDITOS.md`.

## Correspondencia con clases POO

| Componente | Responsabilidad |
|---|---|
| `DigitalWorld` | MDP, acciones, modelo de transiciones y simulación |
| `MonteCarloAgent` | Control MC on-policy First-Visit ε-greedy, sin acceso a valores esperados |
| `ValueIterationAgent` | Valor y política óptima mediante Bellman |
| `evaluate` | Evaluación independiente, medidas de respaldo y retornos |
| `curvas_aprendizaje_v011.py` | Experimento por presupuestos, semillas y reportes |
| `verificar_sin_librerias_rl.py` | Auditoría estática de bibliotecas RL prohibidas |
| `test_academic_v011.py` | Validación de entrenamientos continuados y del auditor |

**Conclusión metodológica:** la v0.11 no introduce ningún algoritmo nuevo de RL; fortalece la evidencia empírica y trazabilidad de los dos algoritmos requeridos en el proyecto final.

## Resultados observados en la corrida incluida

Se utilizaron cinco semillas (41–45), 200 episodios de evaluación por método/semilla/punto de control y la política DP precomputada. **No se estimó una significación estadística entre algoritmos.**

| Episodios MC | Victorias MC (media ± DE) | Victorias DP (media) | Cobertura MC (media) | Tasa de uso de respaldo MC (media) |
|---:|---:|---:|---:|---:|
| 500 | 14,9 % ± 3,1 pp | 96,0 % | 4,9 % | 15,90 % |
| 2.000 | 41,4 % ± 8,7 pp | 96,0 % | 11,3 % | 5,20 % |
| 5.000 | 63,6 % ± 7,0 pp | 96,0 % | 16,8 % | 1,62 % |
| 10.000 | 76,5 % ± 6,8 pp | 96,0 % | 21,2 % | 0,57 % |
| 20.000 | **82,6 % ± 4,6 pp** | 96,0 % | **25,7 %** | **0,19 %** |

En este experimento MC aumentó su tasa media de victoria al aumentar la experiencia y redujo el uso de acciones de respaldo en estados desconocidos. No obstante, se observan diferencias entre semillas y la tasa media de éxito continúa por debajo de DP con 20.000 episodios. La política MC principal de v0.9 fue entrenada con 60.000 episodios; sus resultados no deben mezclarse con los de esta curva de cinco semillas sin indicar el diferente presupuesto de entrenamiento.

Para una presentación inmediata se incluyen además `convergencia_v011.png` y `cobertura_v011.png`, convertidos desde los SVG de esta ejecución. La generación programática reproducible requiere solo Python estándar (SVG); las imágenes PNG son una comodidad de visualización.
