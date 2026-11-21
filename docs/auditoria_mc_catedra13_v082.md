# Auditoría académica Monte Carlo — versión 0.8.2

**Asignatura:** COM50100, Aprendizaje Reforzado (UOH).  
**Método implementado:** control Monte Carlo **on-policy, first-visit, ε-greedy**, sin Exploring Starts.  
**Método comparativo:** Programación Dinámica mediante **Value Iteration**.

## 1. Trazabilidad al material docente

- **Cátedra 13: Monte Carlo Methods III**, profesor Matías Pastene, octubre de 2026, **diapositiva 8**: algoritmo *On-policy first-visit MC control (for ε-soft policies)*.
- **Bibliografía obligatoria del programa:** Sutton y Barto (2018), *Reinforcement Learning: An Introduction*, 2.ª ed., **capítulo 5**. El programa también enumera Bertsekas (2017), *Dynamic Programming and Optimal Control*, vol. I, y Bertsekas y Tsitsiklis (1996), *Neuro-Dynamic Programming*. Para Monte Carlo, la fuente principal empleada es Sutton y Barto.
- No se utilizan **Q-learning, SARSA, TD(0), función aproximadora, redes neuronales ni librerías RL** en el motor del proyecto.

## 2. Definición de las operaciones

Para cada episodio completo, generado con la política ε-greedy actual:

1. Iniciar `G = 0` al final del episodio.
2. Recorrer sus pasos en orden inverso: `G = gamma * G + recompensa`.
3. **Actualizar solo la primera aparición cronológica** de cada par `(estado, acción)` dentro de ese episodio. El código recorre después los pares de adelante hacia atrás para comprobar la condición *first visit*.
4. Calcular incrementalmente el promedio `Q(s,a) ← Q(s,a) + (G - Q(s,a))/N(s,a)`.
5. Generar el próximo episodio con la política ε-greedy sobre la tabla `Q` actualizada.

La probabilidad de escoger una acción aleatoria es `ε`; si no ocurre la exploración, se elige una acción con el mayor `Q(s,a)` actual. Entre las acciones greedy empatadas, el agente realiza un desempate aleatorio durante el entrenamiento.

Con `ε=0,15` y `|A(s)|` acciones legales, cada acción tiene al menos probabilidad `ε/|A(s)|` de ser seleccionada (política ε-suave).

**Parámetros del entrenamiento principal:** `γ=0,95`, `ε=0,15`, semilla 42, 90.000 episodios, máximo 80 turnos.

## 3. Correcciones realizadas

### Episodios truncados

En la versión 0.8.1, el programa procesaba como si fueran retornos completos los episodios detenidos por `max_steps=80`. Ahora los episodios truncados se **registran**, pero **no actualizan Q**; no se inventa una recompensa terminal ni se aplican técnicas de bootstrapping ajenas a Monte Carlo episódico. Esto es un compromiso conservador que evita confundir un corte artificial con una condición terminal real. El número de truncamientos se informa por separado.

### Cobertura y acciones de respaldo

En evaluación, si una política Monte Carlo no conoce un estado, el juego conserva la selección de la primera acción legal para mantener el comportamiento anterior, **pero ahora registra**:

- Cantidad de acciones de respaldo.
- Episodios en los que se utilizó al menos una acción de respaldo.
- Estados distintos desconocidos encontrados durante la evaluación.
- Fracción de decisiones realizadas por respaldo.

Se reporta asimismo la cobertura de **estados alcanzables**: estados distintos visitados y actualizados por MC divididos por la cantidad de estados de la política DP. La cobertura no implica conocer la acción óptima ni equivale a convergencia.

### Multi-semilla

El experimento repetible de `scripts/auditoria_academica_v082.py` ejecuta múltiples entrenamientos Monte Carlo independientes con distintas semillas, evalúa cada uno y exporta:

- `resultados_por_semilla.csv` — rendimiento, retorno descontado, cobertura y respaldo por semilla.
- `aprendizaje_por_bloques.csv` — progresión de la tasa de victoria y recompensa durante el entrenamiento.
- `resumen_multisemilla.json` — media, desviación estándar descriptiva y parámetros.
- `comparacion_multisemilla.svg` — gráfico que puede abrirse en un navegador.

**Nota sobre comparabilidad:** la política DP almacenada fue calculada con `γ=0,95`. Debe recalcularse si cambia ese parámetro. Las corridas multisemilla incluidas se hacen con **10.000 episodios por semilla**, no 90.000, para ser reproducibles rápidamente en otros computadores. No deben confundirse sus resultados con la política MC principal ya entrenada durante 90.000 episodios.

## 4. Reproducir la auditoría

En PowerShell, desde la carpeta extraída `digimon_rpg_rl`, después de instalar el proyecto:

```powershell
.\.venv\Scripts\python.exe scripts\auditoria_academica_v082.py --seeds 41,42,43,44,45 --mc-episodes 10000 --eval-episodes 300
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Reentrenamiento íntegro de MC para reproducir la política incluida:

```powershell
.\.venv\Scripts\python.exe scripts\retrain_mc_v082.py
```

## 5. Interpretación prudente

- Los resultados de evaluación tienen variabilidad estocástica. Una sola semilla no es una estimación precisa del comportamiento general.
- La comparación de distintos métodos se realiza **en el mismo mundo** y con las mismas semillas de evaluación dentro de cada repetición. Las acciones pueden alterar el consumo de números aleatorios, por lo que esto no implica compartir trayectorias idénticas.
- Value Iteration utiliza el modelo de transición explícito y MC aprende de episodios muestreados. Esta diferencia explica parte de sus diferentes requisitos de datos, pero no prueba una superioridad universal de un método.
- Reportar tiempo, recompensa, victorias, truncamientos y cobertura conjuntamente evita conclusiones basadas solo en el porcentaje de victorias.

## 6. Referencias

1. Pastene Orellana, M. (2026). *Monte Carlo Methods III*. Cátedra 13, COM50100, Universidad de O’Higgins, diapositiva 8.
2. Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning: An Introduction* (2.ª ed.), capítulo 5. MIT Press.
3. Universidad de O’Higgins (2026). *Planificación de curso COM50100 Aprendizaje Reforzado*, sección V: bibliografía y recursos obligatorios.

## 7. Mediciones de referencia registradas en v0.8.2

**Políticas principales:** DP ya guardada; MC reentrenado con **90.000 episodios** (semilla 42). Evaluación con 500 partidas por método, semilla 2042: **DP 93,6 % de victorias (468/500)** y **MC 87,4 % (437/500)**. Monte Carlo visitó y actualizó **18.427 estados** y **42.975 pares (s,a)**. De los 90.000 episodios del entrenamiento, **0 fueron truncados**. Durante esas 500 partidas de evaluación no se requirió respaldo, aunque la política solo cubre ~37,95 % de todos los estados alcanzables.

**Experimento multisemilla de auditoría:** semillas MC 41, 42, 43, 44 y 45, **10.000 episodios por semilla**, 300 partidas por algoritmo y semilla (1.500 por método en total). Medias de las cinco tasas por semilla: **Value Iteration 94,20 % (desviación estándar 1,45 puntos porcentuales)**, **MC 70,47 % (desviación estándar 3,41 puntos)**; cobertura de estados MC media **22,69 %**, uso de respaldo medio **0,58 % de las acciones**. Ningún episodio del entrenamiento MC de las cinco semillas resultó truncado. Estas son estadísticas descriptivas, no demostraciones de convergencia ni una comparación a igual presupuesto computacional.
