# Digimon RPG — La corrupción del Mundo Digital · v0.22

Proyecto individual para **COM50100 – Aprendizaje Reforzado**, en Python con Programación Orientada a Objetos. Se comparan **Value Iteration** y **Monte Carlo on-policy First-Visit ε-greedy** (Cátedra 13) sobre el mismo MDP finito episódico. No se usan bibliotecas de aprendizaje reforzado.


## Repositorio público y descarga

**Entrega del curso:** [https://github.com/xZero-exe/Digimon-RPG-COM50100](https://github.com/xZero-exe/Digimon-RPG-COM50100). Autor: Diego Droguett González.

Para Windows: pulsa **Code → Download ZIP**, extrae todo y abre `JUGAR_WINDOWS.bat`. Conserva `assets/`, `politicas/` y `resultados/` junto al código. Python 3.11 o superior; el primer inicio instala las dependencias.

**Créditos:** [artistas de Digidex, fuentes y recursos del proyecto](CREDITOS.md).

**Distribución de los archivos:** este repositorio conserva el código, todos los recursos necesarios para ejecutar el juego, los informes y los resultados numéricos. El [ZIP completo de Releases](https://github.com/xZero-exe/Digimon-RPG-COM50100/releases) conserva además las capturas, videos y animaciones de versiones históricas. [Detalle del archivo histórico](ARCHIVO_HISTORICO.md).

## Edición actual v0.22: Digidex y diario de aventura

- **F7:** once fichas de Digimon canónicos con sprites, técnicas oficiales, valores del RPG y fuente de la enciclopedia.
- **Tab:** diario de la aventura actual; al terminar aparece automáticamente un resumen de ruta, formas, recursos, recompensa y retorno.
- **T · Ver decisión:** consulta en el laboratorio el estado previo a una decisión destacada. Esc vuelve al resumen.

**197 pruebas aprobadas, sin omisiones.** Se conserva el MDP v0.21: nueve regiones, catorce conexiones, siete enemigos y **85.609 estados alcanzables no terminales más dos terminales**. Modelo, imágenes, algoritmos, políticas y curvas de aprendizaje mantienen sus hashes de v0.21.1. La edición pública actualiza únicamente créditos y documentación; no se reentrenó ningún agente.

Extrae todo el ZIP en una carpeta nueva y abre `JUGAR_WINDOWS.bat` con Python 3.11 o superior. El primer inicio instala las dependencias y requiere Internet. `VALIDAR_WINDOWS.bat` realiza dieciséis pasos; **la ejecución del juego en Windows fue confirmada por Diego**. La evidencia automatizada incluida proviene de Linux/SDL dummy; esa confirmación manual no equivale a un registro de la batería completa en Windows.

Guía, fuentes y limitaciones: [Digidex y diario v0.22](docs/digidex_diario_v022.md). Se conservan los desvíos y el balance de [v0.21](docs/rutas_v021.md) y la [corrección de Guardromon](docs/correccion_guardromon_v0211.md).

Los bloques siguientes y el Word v0.19 son **históricos**. Sus cifras de estados, políticas y entrenamiento no describen esta edición; el informe final v0.22 ya integra la evidencia actual. Los avisos de publicación de esos documentos históricos quedan sustituidos por los créditos actuales.

## Informe de la entrega

El informe actualizado conserva el formato académico de las tareas del curso y utiliza las reglas y resultados actuales:

- [Informe final PDF](docs/Informe_Final_Digimon_RPG_v022.pdf)
- [Informe editable Word](docs/Informe_Final_Digimon_RPG_v022.docx)

La confirmación de ejecución manual en Windows está en `resultados/cierre_informe_v022/cierre_documental.json`. Las pruebas automatizadas anteriores mantienen su plataforma y fecha originales. La edición pública incluye código, recursos, políticas, resultados e informe. Los autores y las fuentes de los sprites se reconocen en [CREDITOS.md](CREDITOS.md), también accesible desde la pantalla C del juego.

## Referencia histórica v0.20: balance de Piedmon y WarGreymon

Piedmon tiene **9 PS**. WarGreymon cuesta **2 EN** y reduce hasta **2 PS** de
daño por golpe (mínimo 1), frente a 1 de MetalGreymon. No hay evolución
obligatoria ni recompensa artificial por elegirla. Las formas menores aún
pueden ganar si la situación lo permite.

**Reglas de v0.20: `v0.20-balance-piedmon`; 60.649 estados no terminales
alcanzables y dos terminales.** DP se recalculó y MC se reentrenó durante
60.000 episodios con semilla 42. El laboratorio T contiene los valores nuevos;
F4 y F5 leen las curvas v0.20 de cinco semillas hasta 20.000 episodios.

Extrae todo el ZIP en una carpeta nueva y abre `JUGAR_WINDOWS.bat`.
**169 pruebas aprobadas, sin omisiones.** `VALIDAR_WINDOWS.bat` tiene doce pasos.
La aceptación nativa de Windows sigue
pendiente; los registros incluidos identifican Linux/SDL dummy.

Detalles, evaluación antes/después y reproducción: [balance v0.20](docs/balance_v020.md).
El informe Word v0.19 y las secciones de versiones anteriores que siguen abajo
son **referencias históricas**: sus cifras de 48.553 estados y sus victorias no
describen estas reglas. Antes de entregar el informe del curso, integrar los
resultados nuevos de `docs/balance_v020.md`. Las políticas anteriores quedan
archivadas en `politicas/historico_v019/` y no se cargan para jugar.

## Historial de versiones

## Nuevo en v0.19: preparación académica

Se conserva el juego v0.18 y se actualiza el informe con las nueve partes de la
pauta, ecuaciones editables y dos figuras. Las curvas de 20.000 episodios por
semilla se distinguen de la política MC jugable de 60.000 episodios.

Informe: `docs/Informe_Final_Digimon_RPG_v019.docx`. Guion de diez minutos:
`docs/guion_presentacion_v019.md`. Matriz de cumplimiento y aceptación Windows:
`docs/cierre_academico_v019.md`.

**161 pruebas de software aprobadas**, más una auditoría documental de fuentes,
estadísticas y estructura. `VALIDAR_WINDOWS.bat` incorpora esa auditoría como
décimo paso. La aceptación nativa Windows y la URL pública de entrega aún deben
registrarse; esta edición está preparada para revisión y pruebas locales.

Extrae todo el ZIP y ejecuta `JUGAR_WINDOWS.bat`. Las reglas, agentes y políticas
no se modifican y no se agrega ningún método de aprendizaje.

## Nuevo en v0.18: sonido y transiciones

**23 efectos originales** para los ataques, recursos, botones, viajes y finales.
**F8** silencia; **F9 / F10** ajustan el volumen. También hay botones permanentes
de audio y una prueba de sonido. Las preferencias se conservan entre sesiones.
En F6 se puede escuchar cada habilidad de forma optativa, sin jugar turnos.

Las regiones se conectan con un fundido breve. **V** ajusta su velocidad y
**Espacio** permite omitirlo, igual que el combate. El audio y el reloj de la
acción se pausan en las pantallas auxiliares. El juego funciona sin dispositivo
de sonido y no incorpora dependencias nuevas.

Se conservan el motor, DP/MC, las políticas y las funciones de v0.17.
**161/161 pruebas aprobadas**, 23 WAV comprobados y 22 capturas nuevas con SDL
dummy en Linux. Extrae todo el ZIP y abre `JUGAR_WINDOWS.bat`; para la prueba
nativa usa «Probar sonido» y después `VALIDAR_WINDOWS.bat` con el juego cerrado.
Consulta `docs/sonido_v018.md`. El video demostrativo también está incluido.

## Nuevo en v0.17: mapa ilustrado

Nuevo paisaje de pixel art para el Mundo Digital, con los caminos recorridos,
el retrato de la forma actual y destinos legales iluminados. En modo manual se
puede pulsar el marcador o la placa de una ruta; los agentes siguen sus políticas.
Los avisos narrativos se muestran en el registro para dejar todo el mapa visible.

Se mantienen las siete regiones y las ocho conexiones del motor. No se cambia el
MDP ni se entrena de nuevo a los agentes. El diagnóstico revisa clics de ruta,
cuatro resoluciones y funcionamiento sin imagen. Consulta `docs/mapa_v017.md`.

Extrae todo el ZIP y abre `JUGAR_WINDOWS.bat`. `VALIDAR_WINDOWS.bat` incorpora
el diagnóstico del mapa como octavo paso. La evidencia incluida corresponde a
Linux/SDL dummy; la prueba nativa requiere ejecutar el BAT en Windows.

Revisión v0.17: **152/152 pruebas aprobadas**, ocho rutas verificadas y 44 capturas
del mapa. Motor, políticas y combate de v0.16 conservados.

## Nuevo en v0.16: combates más expresivos

Daño y curación flotantes, cambios de energía, barras animadas y destellos de
impacto. Se distinguen tu acción, el contraataque y su cancelación. Los avisos de
ataques cargados sugieren una respuesta sin decidir por el jugador.

**V** alterna animación normal, rápida ×2 o sin animación. **Espacio** o el botón
«Omitir animación» terminan solo la presentación del turno. **+ / −** ajustan el
ritmo automático. Las pantallas auxiliares detienen la secuencia mientras están abiertas.

Continúa desde v0.15 con todos sus recursos y funciones. El MDP y las políticas
se conservan. Extrae todo el ZIP y abre `JUGAR_WINDOWS.bat`. Consulta
`docs/combate_v016.md` y ejecuta `VALIDAR_WINDOWS.bat` para la prueba en Windows.

Revisión general: **145/145 pruebas aprobadas**, auditoría sin bibliotecas RL y
50 capturas nuevas de Pygame real con SDL dummy en Linux. La prueba nativa en
Windows requiere ejecutar el BAT en ese sistema.

## Nuevo en v0.15: fondos del Mundo Digital

Siete escenarios nuevos de pixel art: aldea, bosque, caverna, pantano, ruinas,
Torre de Datos y fortaleza. Se integran en las escenas de aventura, el menú y F6.
El encuadre conserva las proporciones; las sombras de contacto son translúcidas.
Se conservan los sprites, las habilidades y las funciones anteriores.

Extrae todo el ZIP y abre `JUGAR_WINDOWS.bat`. La guía visual está en
`docs/fondos_v015.md` y el diagnóstico de 35 capturas en
`scripts/validar_fondos_v015.py`, también incluido en `VALIDAR_WINDOWS.bat`.
**136/136 pruebas automatizadas aprobadas** y auditoría estática sin librerías RL.
Las verificaciones de esta entrega corresponden a Linux/SDL dummy; la prueba
nativa en Windows requiere ejecutar ese BAT en tu equipo.

## Corrección v0.14.1: ataques básicos con sprites

La auditoría encontró que Atacar, Ataque especial e Interrumpir tenían `effect=None`, por lo que usaban las líneas de respaldo de la vista. Ahora disponen de tres atlas propios, con cuatro fotogramas cada uno. La galería F6 incluye **13 efectos y 52 fotogramas**.

Los tres nuevos efectos son compartidos por las cuatro digievoluciones para esas acciones generales. Sus técnicas exclusivas conservan sus animaciones anteriores. No cambia el daño, el costo ni la probabilidad de ninguna acción.

Se revisan los tres ataques en las cuatro formas con Pygame real; el diagnóstico está en `scripts/validar_basicos_v0141.py`. La guía de esta corrección es `docs/correccion_ataques_basicos_v0141.md`.

## Nuevo en v0.14: habilidades animadas y galería F6

- **10 habilidades, 40 fotogramas:** Baby Flame, Mega Flame, Giga Destroyer, Terra Force, Electric Shock, Goblin Strike, Haouken, Death Claw, Spiral Sword y Trump Sword.
- **F6:** galería interactiva, con selección por clic o flechas y repetición con Espacio.
- **Combate:** acción y contraataque se muestran por separado. Espacio termina la animación sin consumir otro turno. El modo automático espera su final.
- **Recursos:** atlas PNG transparentes en `assets/effects/`; referencias y uso en `docs/habilidades_8bits_v014.md`.
- **Verificación:** 132/132 pruebas aprobadas; diagnóstico gráfico de los diez efectos incluido en `VALIDAR_WINDOWS.bat`. La evidencia de esta entrega corresponde a Linux/SDL dummy; queda pendiente la ejecución nativa en Windows.

Extrae **todo** el ZIP en una carpeta nueva y ejecuta `JUGAR_WINDOWS.bat`. Se conservan las políticas, el modelo, la arquitectura POO y las funciones de v0.13.

## Nuevo en v0.13

Continuación directa de v0.12. Ventana ajustable al escritorio, redimensionado con clics correctos y pantalla completa con `F11`. Los combates con más de cuatro acciones usan dos filas; F4 y F5 tienen botones en la cabecera. Los gráficos ahora posicionan sus puntos según el número real de episodios.

**Inicio en Windows:** extrae todo el ZIP y ejecuta `JUGAR_WINDOWS.bat`. Requiere Python 3.11 o superior e Internet para la instalación inicial. Después de cerrar el juego, ejecuta `VALIDAR_WINDOWS.bat` para registrar las comprobaciones en tu equipo.

**Evidencia de esta entrega:** 121/121 pruebas aprobadas, auditoría estática sin librerías RL y 24 capturas de Pygame real con SDL dummy en Linux. **La prueba nativa y la aceptación visual en Windows están pendientes**; sigue `docs/validacion_windows_v013.md`.

**Informe iniciado:** `docs/Informe_Final_Digimon_RPG_Borrador_v013.docx`, con fuente Markdown y las nueve secciones exigidas por el profesor. El cierre está en `docs/plan_informe_final_v013.md`. Es una versión preliminar para revisión.

No se modifican las reglas ni las políticas de los agentes. El experimento de curvas sigue siendo v0.11 y la política MC para jugar sigue usando 60.000 episodios. Consulta `CAMBIOS_v0_13.md`.

## Nuevo en v0.12: resultados y presentación desde Pygame

- **F4 — Resultados académicos** desde menú o partida: muestra gráficos reales del experimento v0.11 (victorias, cobertura MC, retorno descontado y uso de acciones de respaldo). Navega con **← / →** o mediante las pestañas. Dibuja las medias de cinco semillas y la dispersión ±1 desviación estándar cuando existe en el archivo original. La referencia DP solo se incluye en las métricas para las cuales se midió.
- **F5 — Presentación guiada**: seis diapositivas dentro del RPG, con objetivo, MDP, métodos de clase, curva, limitaciones y enlaces para jugar con DP (`F1`) o MC (`F2`). Navega con **← / → / Espacio**; `Esc` vuelve sin perder la partida.
- **T — Laboratorio de políticas** sigue disponible en el juego para inspeccionar decisiones reales y valores Q.
- **Datos originales:** `resultados/convergencia_v011/curvas_resumen.csv` y `resumen_v011.json`; no hay entrenamiento ni estimaciones fabricadas durante el renderizado. Si faltan esos archivos, el juego sigue funcionando, aunque el panel avisa que no hay resultados.
- **Aclaración metodológica:** la gráfica compara entrenamientos MC de **hasta 20.000 episodios**, no la política principal MC guardada en `politicas/mc.json`, entrenada con **60.000**. La curva muestra aprendizaje observado, no demuestra convergencia matemática.
- **Pruebas:** se añadieron diez verificaciones de lectura CSV/JSON, métricas, integridad y navegación; 114 pruebas totales aprobadas en este entorno. Pygame no está disponible para validar visualmente la ventana aquí.

Consulta `docs/guion_presentacion_v012.md` y `CAMBIOS_v0_12.md`.

## Nuevo en v0.11: curvas de aprendizaje y auditoría de bibliotecas RL

El proyecto sigue usando **solo dos algoritmos RL implementados desde cero**:
**Value Iteration** y **Monte Carlo on-policy First-Visit con ε-greedy**,
según las cátedras COM50100 y el capítulo 5 de Sutton y Barto. NumPy acelera
operaciones numéricas de Bellman; **no es una biblioteca de RL**. Pygame solo dibuja.

Se añadió un estudio de convergencia por presupuesto de entrenamiento de MC,
con checkpoints acumulativos (500, 2.000, 5.000, 10.000 y 20.000 episodios)
y cinco semillas de entrenamiento. Se guardan gráficas SVG, datos CSV y resumen JSON.
Un entrenamiento dividido en bloques ahora conserva numeración continua y
produce los mismos Q y conteos que un entrenamiento sin interrupciones.

**Auditar que no se importan librerías RL**: en Windows también puedes abrir `VERIFICAR_SIN_RL_WINDOWS.bat` (con el proyecto extraído).

```powershell
.\.venv\Scripts\python.exe scripts\verificar_sin_librerias_rl.py
```

**Repetir las curvas** (el ZIP ya contiene los resultados):

```powershell
.\.venv\Scripts\python.exe scripts\curvas_aprendizaje_v011.py --seeds 41,42,43,44,45 --checkpoints 500,2000,5000,10000,20000 --eval-episodes 200
```

Abre `docs/curvas_convergencia_v011.md` para metodología, ecuaciones,
interpretación, limitaciones y rutas de archivos.

**Resultados de cinco semillas (v0.11):** Monte Carlo aumentó de 14,9 %
de victorias con 500 episodios a 82,6 % con 20.000 episodios,
frente al 96,0 % de la política DP como referencia. Desviación estándar
entre semillas al final: 4,6 puntos porcentuales. Se incluyen gráficos
SVG y PNG en `resultados/convergencia_v011/`. Las funciones del RPG,
la v0.10 de laboratorio visual y los sprites locales se conservan.

## Nuevo en v0.9: habilidades por digievolución

| Digimon | Técnica | Energía | Daño base | Precisión | Efecto |
|---|---|---:|---:|---:|---|
| Agumon | Baby Flame | 1 | 2 | 90 % | Ataque preciso |
| Greymon | Mega Flame | 2 | 4 | 80 % | Cancela el ataque anunciado si acierta |
| MetalGreymon | Giga Destroyer | 2 | 5 | 80 % | Ignora hasta 2 puntos de armadura |
| WarGreymon | Terra Force | 3 | 8 | 85 % | Ignora hasta 3 puntos de armadura y cancela ataque anunciado |

La nueva acción es `Action.TECHNIQUE`. No sustituye al ataque normal ni al ataque especial genérico de menor costo. El agente selecciona la técnica según salud, energía, forma, armadura enemiga y ataques anunciados. **Todos los resultados probabilísticos están definidos exclusivamente en `DigitalWorld.transitions()`**, que comparten ambos métodos. Los efectos ocurren dentro del turno, por lo que **no agregan variables al estado**.

## Cómo jugar en Windows

1. **Extrae completamente el ZIP**; no ejecutes el `.bat` desde la ventana del archivo comprimido.
2. Abre la carpeta `digimon_rpg_rl` que contiene `pyproject.toml`, `JUGAR_WINDOWS.bat`, `src`, `assets` y `politicas`.
3. Ejecuta `JUGAR_WINDOWS.bat`. Se requiere Python **3.11+**. El iniciador crea `.venv` e instala **Pygame y NumPy** si faltan; necesita conexión durante esa instalación.
4. `F1` juega la política de Programación Dinámica, `F2` la de Monte Carlo y `F3` permite elegir manualmente las acciones. `1–7` selecciona acciones, `Espacio` avanza, `A` activa reproducción automática, `R` reinicia y `H` muestra ayuda.

Desde PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[game]"
.\.venv\Scripts\python.exe -m digimon_rl.play
```

## Modelo MDP y algoritmos

El estado sigue siendo `GameState(zone, hp, energy, enemy_hp, evolved, potion, enemy_charging, data_core, xp, trained)`, **10 componentes, 48.553 estados no terminales alcanzables** y dos estados terminales. Parámetros: `γ=0.95`, `ε=0.15`. La experiencia y el entrenamiento de habilidades de v0.8 permanecen.

- **Value Iteration**: política completa usando el modelo probabilístico y ecuación de Bellman. Implementación tabular, ahora acelerada mediante vectores NumPy (`bincount` y `maximum.reduceat`) para evitar repetir miles de bucles Python; el algoritmo matemático no cambió.
- **Control MC First-Visit on-policy ε-greedy**: aprende Q(s,a) por promedio incremental de retornos de episodios **completos**. Los truncamientos se registran y no actualizan Q. Los estados desconocidos usan primera acción legal, contabilizada como respaldo durante la evaluación.
- Las políticas persistidas en `politicas/` usan **formato 6, reglas v0.9**. Las políticas v0.8 son rechazadas para evitar evaluar modelos antiguos bajo reglas nuevas.

**Se incluyen políticas actualizadas** (`dp.json` y `mc.json`), así que no necesitas entrenar para abrir el juego. La política MC principal utiliza 60.000 episodios, semilla 42. Para generar nuevas políticas:

```powershell
.\.venv\Scripts\python.exe -m digimon_rl.train --episodes 60000 --seed 42
```

### Evaluación principal reproducible

En 500 episodios por política, semilla 2042:

| Métrica | Value Iteration | Monte Carlo |
|---|---:|---:|
| Victorias | 471/500 (94,2 %) | 453/500 (90,6 %) |
| Retorno descontado medio | 86,10 | 79,41 |
| Estados con técnica elegida en la política | 3.732 | 1.484 |
| Acciones de respaldo en evaluación | 0 | 2 |

Son resultados de **una muestra con semilla fija**. No constituyen garantía estadística de superioridad universal; la comparación multisemilla está en `resultados/auditoria_v0_9/`.

### Auditorías y tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts\auditoria_academica_v09.py --seeds 41,42,43,44,45 --mc-episodes 10000 --eval-episodes 300
```

**121/121 pruebas automatizadas aprobadas en v0.13**, incluidas las pruebas anteriores de técnicas y las nuevas regresiones de geometría y renderizado real de SDL. La ejecución nativa de la ventana en Windows sigue pendiente; la evidencia incluida identifica Linux y SDL dummy.

## Arquitectura POO

- `domain.py`: enumeraciones, estado inmutable y episodios.
- `techniques.py`: clase `Technique` inmutable y catálogo de cuatro habilidades.
- `environment.py`: legalidad, transición y muestreo estocástico; fuente única de verdad MDP.
- `agents.py`: Value Iteration y Monte Carlo; NumPy se usa solo para cálculo numérico en DP.
- `policy_io.py`: carga/guardado versionado de políticas.
- `session.py`: controlador de aventuras y mensajes de técnicas.
- `presentation.py`: narrativa y pantallas.
- `academic_dashboard.py`: lectura, validación y métricas de experimentos CSV/JSON (sin Pygame ni RL).
- `gui/`: Pygame, HUD, sprites y efectos.
- `tests/`: pruebas unitarias de algoritmos, estados, sesiones, instalación y técnicas.
- `scripts/`: evaluación y auditoría multisemilla sin bibliotecas de RL.

## Fuentes académicas

- Matías Pastene (2026), *Cátedra 13 – Monte Carlo Methods III*, Universidad de O'Higgins, especialmente el pseudocódigo *On-policy first-visit MC control*.
- Sutton, R. S. y Barto, A. G. (2018), *Reinforcement Learning: An Introduction*, 2.ª ed., capítulo 5.
- Bertsekas, D. P. (2017), *Dynamic Programming and Optimal Control*, 4.ª ed., vol. I.
- Bertsekas, D. P. y Tsitsiklis, J. N. (1996), *Neuro-Dynamic Programming*.

## Créditos visuales

Los once sprites de los personajes proceden de [Digidex](https://github.com/SergioGranSol/digidex). Se reconoce a SergioGranSol y a todos los artistas y colaboradores acreditados por su colección. La lista con sus enlaces y la procedencia individual de los PNG está en [CREDITOS.md](CREDITOS.md). Los derechos del arte permanecen con sus creadores.

## v0.10: Laboratorio de políticas (uso académico)

Durante cualquier aventura pulsa **T** o el botón **T Analizar**. La pantalla muestra
las acciones legales, la recomendación de Value Iteration y la política greedy
aprendida por Monte Carlo, además de sus valores tabulares:

- **Q\*(s,a) DP**: se recalcula con la ecuación de Bellman, las transiciones
  conocidas del MDP y los valores óptimos V\*(s) obtenidos por Value Iteration.
- **Q_MC(s,a)**: promedio *First-Visit* de los retornos descontados observados
  realmente durante 60.000 episodios on-policy ε-greedy, junto al número de visitas.
  Si un par (s,a) no fue visitado, aparece como **No visitado**, no como Q=0.
- **Cobertura MC**: proporción de estados alcanzables con acción guardada;
  **no es** un índice de convergencia ni garantía de optimalidad.
- **Flechas izquierda/derecha**: revisar estados de turnos previos sin alterar el juego.
- **T / Esc / Enter**: volver a la aventura; la reproducción automática queda pausada.

Los datos se almacenan en `politicas/analisis_v010.json.gz` y se validan mediante
SHA-256 de las dos políticas. Si el archivo falta o es incompatible, el RPG sigue
funcionando, pero no muestra valores estimados que no pueda respaldar.

### Consulta sin entorno gráfico

```powershell
python -m digimon_rl.inspect_policies
python -m digimon_rl.inspect_policies --csv resultados/ejemplo_valores_q.csv
```

**Reproducibilidad:** los datos fueron reconstruidos exactamente con el MDP v0.9,
γ=0.95, MC ε=0.15 y semilla=42, verificando igualdad de ambas políticas
respecto a los JSON de la v0.9. El motor, el método MC y las reglas del RPG
no cambiaron; esta versión es una mejora de visualización y trazabilidad.
El renderizado de Pygame debe verificarse también en Windows.

Validación de esta corrección: **135/135 pruebas aprobadas** y diagnóstico de ataques básicos aprobado con Pygame real en Linux/SDL dummy.
