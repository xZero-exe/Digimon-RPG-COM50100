# Mapa ilustrado del Mundo Digital — v0.17

Continuación de v0.16. Conserva el combate expresivo, los siete fondos, los trece
efectos de ataques, las políticas y las pantallas F4, F5, F6 y T.

## Qué cambia

El mapa combina un paisaje de pixel art con marcadores y caminos dibujados por
el programa. La ilustración contiene terreno: bosque, montañas de cristales,
pantano, ruinas, zona tecnológica y tierras corrompidas. Las ocho conexiones,
los nombres y las zonas pulsables pertenecen al código y se contrastan con el MDP.

| Señal | Significado |
| --- | --- |
| Retrato del Digimon, anillo y «ACTUAL» | Ubicación y forma actuales del jugador |
| Camino dorado | Conexión realmente recorrida en esta aventura |
| Camino cian / «ELEGIR RUTA» | Destino disponible en modo manual |
| «RUTA POSIBLE» | Destino legal mostrado sin habilitar el clic, por ejemplo para un agente |
| Marca verde / «DESPEJADA» | Región cuyo guardián fue derrotado |
| «SIN VISITAR» | Región que todavía no se ha visitado en esta aventura |

Los caminos recorridos se obtienen del historial ordenado de estados de la partida.
Al pasar el puntero por una región se conserva la información de su guardián y
sus riesgos; la caverna indica la energía adicional y la posibilidad de emboscada.
No se deducen a partir de dos regiones que casualmente figuren como visitadas.
La ubicación se resalta con un pulso y las rutas manuales con un punto móvil.
La opción V «sin animación» deja estos adornos estáticos.

La cifra de regiones visitadas no es una barra obligatoria de completar: el juego
tiene ramas alternativas y una aventura normal no visita las siete regiones.

## Elegir un camino

En modo manual se puede pulsar el marcador o la placa del destino iluminado.
La aldea permite Bosque o Caverna; el Pantano despejado permite Ruinas o Torre.
También se habilita el avance a la región siguiente desde Bosque, Caverna,
Ruinas y Torre una vez despejados. La fortaleza no añade una salida nueva:
se termina la aventura mediante las acciones existentes del panel.

Un clic sobre un avance normal ejecuta **Avanzar**. **Buscar recursos** sigue
siendo una decisión explícita en el panel, con su propio riesgo y recompensa.
El mapa no escoge esa alternativa por el jugador. Las políticas DP y MC eligen
sus acciones como antes; sus mapas muestran el recorrido y no permiten intervenir
mediante los destinos de ruta.

Durante el combate, la animación del turno, los diálogos o el final de la aventura
no se habilitan rutas manuales. Un segundo clic que conserve un botón de la imagen
anterior se ignora si su acción ya no es legal; no consume otro turno ni otro muestreo.

## Narración y funcionamiento

Los avisos de región aparecen temporalmente en el registro de aventura, debajo
del turno y la recompensa. Se cierran con X o Espacio, como antes. La descripción
se distribuye en líneas para dejar visibles el mapa completo y ambas rutas.

La imagen se incluye en `assets/maps/world_map.png`, con carga local y caché,
vecino más cercano y recorte que conserva sus proporciones. Si falta o no puede
cargarse, se dibuja un mapa esquemático con los mismos caminos y controles.

El arte se creó con la herramienta integrada de generación de imágenes para
este proyecto. Es una ilustración nueva de estética retro, no un mapa oficial
de Digimon. La solicitud exacta está en `assets/maps/prompt_v017.txt`; dimensiones
e integridad en `assets/maps/manifest_v017.json`. Se solicitó terreno panorámico
opaco, sin caminos, rótulos, nodos, personajes ni interfaz; el programa incorpora
esos elementos por separado. No se impone una paleta técnica de consola de 8 bits.

## Validación

Resultado: **152/152 pruebas aprobadas**, 71 archivos Python auditados sin
bibliotecas RL y **44 capturas** del diagnóstico nuevo. La comprobación frente
a v0.16 confirma que se conservan los archivos del motor, políticas, recursos
anteriores, feedback de combate y resultados académicos.

`tests/test_world_map_v017.py` contrasta las ocho conexiones con las transiciones
del motor, comprueba las acciones originales de las bifurcaciones, la ausencia de
destinos durante el combate y la lectura del recorrido desde el historial.

`scripts/validar_mapa_v017.py` usa Pygame real para revisar las siete regiones,
las cuatro formas, los ocho clics de ruta, DP/MC en solo lectura, bloqueos durante
la animación, cuatro resoluciones, narración y respaldo sin imagen. También
comprueba botones sin superposición y que dibujar no modifica el episodio ni el RNG.

La vista previa final corresponde a una trayectoria real con semilla 42: acciones
de la política DP guardada ejecutadas explícitamente en modo manual hasta despejar
el Pantano. Es una demostración de interfaz, no un experimento nuevo de aprendizaje.

Para probar en Windows: extraer todo el ZIP, abrir `JUGAR_WINDOWS.bat` y después
ejecutar `VALIDAR_WINDOWS.bat` con el juego cerrado. El mapa es el octavo paso.
La evidencia entregada se ejecutó en **Linux con SDL dummy**; la prueba nativa
en Windows requiere ejecutar ese BAT en un equipo Windows.

Prueba manual sugerida: elegir las rutas desde el mapa, revisar el recorrido dorado,
verificar el marcador al digievolucionar, abrir F4/F5/F6/T y regresar, redimensionar
la ventana y comprobar que los avisos ya no cubren el camino inferior.
