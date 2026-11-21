# Digimon RPG — La corrupción del Mundo Digital

UNIVERSIDAD DE O’HIGGINS

Ingeniería Civil en Computación

Aprendizaje Reforzado COM50100

Digimon RPG
La corrupción del
Mundo Digital

Comparación de Programación Dinámica y control Monte Carlo

Estudiante   Diego Droguett González

Profesor   Matías Pastene Orellana

Fecha   4 de noviembre de 2026

Versión del proyecto   0.13 sobre la base 0.12

Informe preliminar para revisión académica

## Índice

Resumen  2

Estado del arte  2

Metodología  3

Resultados  5

Discusión  6

Conclusión  6

Referencias  6

## Resumen

Este proyecto compara Value Iteration y control Monte Carlo on-policy First-Visit con exploración ε-greedy en un RPG episódico inspirado en Digimon. El agente conduce a Agumon a través de siete regiones, administra salud y energía, elige rutas y decide cuándo combatir, curarse o digievolucionar. El modelo contiene 48.553 estados no terminales alcanzables y dos estados terminales. La implementación utiliza Python y Programación Orientada a Objetos; los dos algoritmos están programados manualmente.

La evaluación incluida utiliza cinco semillas de entrenamiento Monte Carlo y presupuestos acumulativos de 500 a 20.000 episodios. En el último punto, Monte Carlo alcanza una tasa media de victoria de 82,6 %, frente a 96,0 % de la política de Programación Dinámica, con 200 partidas de evaluación por método y semilla. La cobertura media de estados de Monte Carlo llega a 25,7 %. Estos resultados muestran una mejora empírica con la experiencia y una diferencia de desempeño dentro del protocolo evaluado; no demuestran convergencia matemática ni superioridad universal. La interfaz permite observar decisiones, inspeccionar valores de acción y presentar los resultados sin ejecutar entrenamiento durante el renderizado.

## Estado del arte

El aprendizaje reforzado estudia decisiones secuenciales guiadas por recompensas. En un MDP finito, la política relaciona cada estado con una distribución sobre las acciones disponibles. La Programación Dinámica aprovecha un modelo conocido de transiciones y recompensas para aplicar las ecuaciones de Bellman; los métodos Monte Carlo estiman retornos a partir de episodios completos [1, capítulos 3–5].

Value Iteration y control Monte Carlo representan dos formas de resolver el mismo problema: planificación con expectativas calculadas desde un modelo y aprendizaje desde experiencia muestreada. La variante empleada en este trabajo corresponde al control on-policy First-Visit para políticas ε-soft desarrollado en la Cátedra 13 [2]. El videojuego funciona como entorno de comparación y como representación de decisiones observables. El alcance de estos antecedentes se limita a los métodos exigidos en COM50100 [3].

## Metodología

### Modelo de decisión

El estado contiene diez componentes. Las variables incluyen todos los recursos y condiciones persistentes que el motor utiliza para generar la siguiente transición; la intención de ataque enemigo se observa antes de decidir. El estado inicial corresponde a la Aldea Digital, con salud 6, energía 3, Agumon, una poción y el resto de recursos en cero. Los estados terminales son victoria y derrota.

| Variable | Interpretación | Dominio nominal no terminal |
| --- | --- | --- |
| L | Región | 7 regiones |
| H | Salud del protagonista | 1 a 6 |
| E | Energía | 0 a 6 |
| V | Salud enemiga | 0 a 6 |
| D | Digievolución | 0 a 3 |
| P | Disponibilidad de poción | 0 o 1 |
| C | Ataque enemigo cargado | 0 o 1 |
| N | Núcleo de datos | 0 o 1 |
| X | Experiencia | 0 a 2 |
| M | Mejora del ataque | 0 o 1 |

El producto de los dominios describe combinaciones nominales, muchas de ellas inalcanzables. La cifra de 48.553 se refiere únicamente a estados no terminales enumerados desde el estado inicial. Las acciones dependen del estado: rutas, exploración de recursos, ataque, ataque especial, técnica de la forma actual, defensa, poción, digievolución, interrupción y entrenamiento.

DigitalWorld.transitions define la distribución de cada transición y su recompensa; DigitalWorld.sample selecciona resultados de esa distribución. Se verifica que las probabilidades de las acciones legales sumen uno. Entre las recompensas se incluyen +100 al completar la aventura, penalización de −80 por muerte y costos y beneficios intermedios establecidos en el motor [4]. El retorno usa descuento γ = 0,95. El límite operativo de 80 turnos se registra como truncamiento y se distingue de alcanzar un estado terminal.

### Programación Dinámica

ValueIterationAgent inicializa los valores en cero y aplica el operador de Bellman hasta que la diferencia máxima entre iteraciones es menor que 10⁻⁸, o se alcanza el máximo de 500 iteraciones. La política selecciona la acción que maximiza la expectativa calculada con el modelo. NumPy se utiliza para agregar operaciones numéricas; no aporta un algoritmo de aprendizaje reforzado [1, 4].

$$
V_{k+1}(s)=\max_a\sum_{s\prime,r}p(s\prime,r\mid s,a)[r+\gamma V_k(s\prime)]
$$

### Control Monte Carlo

MonteCarloAgent genera episodios con una política ε-greedy respecto de Q, con ε = 0,15. La elección exploratoria es uniforme entre las acciones legales; durante la explotación se elige entre las acciones con mayor Q. Esta exploración garantiza una probabilidad positiva para cada acción legal, pero no garantiza haber visitado todos los pares estado acción con un presupuesto finito.

Al terminar un episodio completo se calculan sus retornos desde el final hacia el inicio. Se recorre luego la trayectoria en orden cronológico y se actualiza únicamente la primera aparición de cada par estado acción. El valor se obtiene mediante una media incremental. N representa el número de retornos utilizados en ese par y el retorno en el terminal es cero [1, 2, 4].

$$
G_t=R_{t+1}+\gamma G_{t+1}
$$

$$
Q(s,a)\leftarrow Q(s,a)+\frac{G_t-Q(s,a)}{N(s,a)}
$$

Los episodios truncados por el límite de pasos se cuentan, pero no actualizan Q. El entrenamiento usa la política ε-greedy y las evaluaciones emplean su versión greedy congelada. El agente no consulta el modelo para calcular expectativas durante el aprendizaje. Para un estado no aprendido se aplica una acción legal de respaldo y se registra su uso.

### Arquitectura orientada a objetos

| Clase | Responsabilidad |
| --- | --- |
| GameState | Estado inmutable con diez variables. |
| DigitalWorld | Acciones, transiciones y muestreo del mismo MDP. |
| ValueIterationAgent | Planificación tabular con el modelo. |
| MonteCarloAgent | Aprendizaje First-Visit desde episodios. |
| AdventureController | Turnos, políticas, historial y fin de la partida. |
| GamePresentation y RPGApp | Navegación, representación visual y entrada. |
| AcademicDashboard y PolicyInspector | Consulta de evidencia y valores almacenados. |

La versión 0.13 adapta el lienzo gráfico a la ventana sin cambiar las variables del estado. La transformación de coordenadas mantiene la correspondencia entre los botones dibujados y el clic del usuario. Los paneles académicos consultan archivos persistidos y no actualizan las políticas.

### Protocolo experimental

Se emplean cinco semillas de entrenamiento independientes: 41, 42, 43, 44 y 45. Cada agente Monte Carlo continúa su entrenamiento en los puntos de control 500, 2.000, 5.000, 10.000 y 20.000 episodios, conservando Q entre puntos. Por cada combinación de método, semilla y punto se ejecutan 200 episodios de evaluación, con un máximo de 80 turnos. Dentro de cada corrida se reutiliza la semilla de evaluación entre métodos y puntos; ello no implica que distintas políticas sigan trayectorias idénticas.

La referencia de Programación Dinámica es la política precomputada para las mismas reglas y γ. Se calculan tasas de victoria, retorno descontado, cobertura de estados y frecuencia de respaldo. La desviación estándar se calcula entre las cinco semillas. El experimento de curvas llega a 20.000 episodios por semilla; la política Monte Carlo incluida para jugar se entrenó por separado con 60.000 episodios y semilla 42. Sus cifras no se mezclan.

## Resultados

| Episodios MC | Victorias MC
media ± DE | Victorias DP
media | Cobertura MC
media | Respaldo MC
media |
| --- | --- | --- | --- | --- |
| 500 | 14,9 ± 3,1 % | 96,0 % | 4,9 % | 15,90 % |
| 2.000 | 41,4 ± 8,7 % | 96,0 % | 11,3 % | 5,20 % |
| 5.000 | 63,6 ± 7,0 % | 96,0 % | 16,8 % | 1,62 % |
| 10.000 | 76,5 ± 6,8 % | 96,0 % | 21,2 % | 0,57 % |
| 20.000 | 82,6 ± 4,6 % | 96,0 % | 25,7 % | 0,19 % |

Tabla 1. Evaluación de las curvas v0.11. La DE de las tasas se expresa en puntos porcentuales. Fuente: curvas_resumen.csv y resumen_v011.json incluidos en el proyecto.

Entre 500 y 20.000 episodios, la tasa media de victoria de Monte Carlo aumenta de 14,9 % a 82,6 %. En el último punto, su desviación estándar es 4,6 puntos porcentuales y la diferencia de las medias respecto de DP es 13,4 puntos porcentuales. El retorno descontado medio final es 65,85 para MC y 88,26 para DP. La cobertura media pasa de 4,94 % a 25,71 % y el uso de respaldo cae de 15,90 % a 0,19 %.

La validación de la interfaz con Pygame 2.6.1 en Linux y SDL dummy permite renderizar las pantallas y ejecutar aventuras completas de ambos agentes. Esta evidencia confirma el funcionamiento en ese entorno; la validación nativa en Windows debe registrarse ejecutando VALIDAR_WINDOWS.bat y completando la revisión visual descrita en la guía incluida.

## Discusión

La mejora observada de Monte Carlo es consistente con una estimación de retornos que se beneficia de más episodios. Sin embargo, el presupuesto de 20.000 episodios deja gran parte del espacio alcanzable sin visitar. Una cobertura baja no impide un buen desempeño desde el inicio fijo: la evaluación puede concentrarse en un subconjunto de estados frecuente bajo la política aprendida. Por la misma razón, la tasa de victoria desde ese inicio no demuestra calidad equivalente en todo el espacio de estados.

La comparación también está condicionada por la información disponible para cada método. DP utiliza el modelo completo y MC aprende desde muestras. El protocolo permite comparar el desempeño de sus políticas dentro del mismo entorno, pero no equipara costo computacional ni acceso a información. Las curvas incluidas reutilizan DP y no constituyen una comparación de tiempos totales de entrenamiento.

Una exploración ε-greedy con ε constante mantiene variación en el comportamiento de entrenamiento. La política greedy empleada al evaluar puede tener un desempeño distinto a esa política de comportamiento. Las desviaciones estándar describen variabilidad entre cinco semillas y no son intervalos de confianza. El experimento tampoco incluye una prueba de significación estadística ni una demostración formal de convergencia.

Los truncamientos por el límite de 80 turnos se contabilizan y se omiten de la actualización Monte Carlo. Si fueran frecuentes, correspondería evaluar el sesgo de utilizar solamente episodios completos. También debe distinguirse un estado no visitado de una acción cuyo valor inicial continúa en cero.

## Conclusión

El proyecto implementa y compara dos métodos del curso dentro de un MDP finito representado como videojuego. La separación entre el motor, los agentes y la interfaz conserva una única definición de reglas para la planificación, el entrenamiento y la visualización. Los resultados incluidos muestran que Monte Carlo mejora con el presupuesto evaluado y reduce su dependencia de acciones de respaldo, mientras que la referencia DP mantiene un desempeño superior en este protocolo.

El cierre requiere registrar la ejecución nativa en Windows y ensayar la presentación de diez minutos con la evidencia reproducible del repositorio público exigido por el curso.

## Referencias

[1] Sutton, R. S. y Barto, A. G. (2018). Reinforcement Learning: An Introduction. Segunda edición. MIT Press. Capítulos 3, 4 y 5.

[2] Pastene Orellana, M. (2026). Cátedra 13 Monte Carlo Methods III. Material docente de COM50100, Universidad de O’Higgins.

[3] Pastene Orellana, M. (2026). Proyecto Final Aprendizaje Reforzado COM50100. Instrucciones de entrega, archivo Final_Project.pdf.

[4] Droguett González, D. (2026). Digimon RPG La corrupción del Mundo Digital. Código Python v0.13, políticas y resultados reproducibles v0.11 incluidos en el paquete del proyecto.
