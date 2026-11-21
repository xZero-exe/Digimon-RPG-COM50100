# Fondos de aventura — v0.15

Continuación de v0.14.1. Se sustituyen visualmente los siete escenarios geométricos
de demostración por fondos nuevos de pixel art, generados para este proyecto.
No requieren descargas durante el juego. Se conservan los fondos de demostración
como respaldo, los personajes de Digidex y los trece efectos de combate.

| Región | Archivo en `assets/backgrounds/` | Dirección visual |
| --- | --- | --- |
| Aldea Digital | village.png | Plaza cálida, casas y árbol antiguo con detalles digitales |
| Bosque | forest.png | Bosque frondoso, claro luminoso y ruinas cubiertas de musgo |
| Caverna | cave.png | Arcos rocosos, cristales cian y minerales ámbar |
| Pantano | swamp.png | Cipreses, niebla y ribera de tierra firme para combatir |
| Ruinas | ruins.png | Columnas antiguas, vegetación y atardecer lavanda |
| Torre de Datos | tower.png | Rotonda tecnológica, circuitos cian y detalles de cobre |
| Fortaleza | fortress.png | Arquitectura oscura, corrupción carmesí y suelo violeta |

## Integración

El render conserva la proporción de cada imagen: amplía hasta cubrir el recuadro y
recorta el sobrante desde el centro. Usa vecino más cercano para mantener los
bordes del pixel art. Las superficies quedan en caché por ruta y tamaño.
El menú utiliza el nuevo bosque, con un sombreado más liviano; la galería F6
también utiliza los fondos nuevos según el enemigo de cada técnica.

Las sombras de contacto son pequeñas y translúcidas, ajustadas a las dimensiones
de los sprites. Reemplazan los óvalos azules opacos que tapaban parte del terreno.
Las reglas, probabilidades, recompensas, estados, políticas y algoritmos de RL
se conservan. El render no avanza turnos ni consume números aleatorios del MDP.

## Probar la entrega

1. Extraer **todo** el ZIP en una carpeta nueva.
2. Abrir `JUGAR_WINDOWS.bat` (Python 3.11 o superior; Internet en la instalación inicial).
3. Iniciar con F3, visitar ambas rutas y la Torre de Datos; recorrer hasta la fortaleza.
4. Abrir F6 y revisar los ataques enemigos para comparar escenarios con efectos activos.
5. Comprobar F11 y redimensionado: personajes, suelo y textos deben conservarse legibles.
6. Cerrar el juego y ejecutar `VALIDAR_WINDOWS.bat` para registrar la prueba nativa.

El diagnóstico `scripts/validar_fondos_v015.py` comprueba los siete recursos,
las cuatro formas sobre cada uno, seis regiones en la galería y el menú: **35 capturas**.
También verifica recorte sin deformación, ausencia de interpolación, caché,
respaldo y conservación del estado/RNG. La evidencia está en `resultados/fondos_v015/`.

Resultado: **136/136 pruebas automatizadas aprobadas**, auditoría estática de 62
archivos Python sin librerías RL y 35 capturas nuevas aprobadas. Las pruebas
anteriores de interfaz, habilidades y ataques básicos también siguen aprobadas.

La validación de esta entrega se ejecutó en **Linux con Pygame real y SDL dummy**.
La ejecución nativa y la aceptación visual en Windows siguen pendientes de realizar
en un equipo Windows; el BAT incluye el nuevo diagnóstico como sexto paso.

## Arte y especificaciones de generación

Los siete PNG se crearon con la herramienta integrada de generación de imágenes.
No son fondos oficiales de Digimon ni imágenes obtenidas de otro videojuego.
Las descripciones de esta sección resumen las especificaciones de diseño;
los hashes y dimensiones de los archivos finales figuran en `assets/backgrounds/manifest_v015.json`.

Especificación común: fondo horizontal 16:9 para combate JRPG lateral, pixel art retro
inspirado en 8 bits, siluetas escalonadas, sombreado por grupos de píxeles, tres
planos de profundidad. Suelo despejado en el 40% inferior; espacio para luchadores
en 28% y 76% del ancho, con los pies aproximadamente al 84% de la altura.
Detalle concentrado en planos lejanos y laterales. Imagen opaca sin personajes,
texto, HUD, bordes o marcas. Evitar pintura suave, desenfoque y render 3D.

Variaciones de escenario: la tabla anterior resume cada solicitud. Se pidieron
paletas verdes y cálidas para la aldea/bosque; índigo, cian y ámbar para caverna;
verde petróleo y musgo para pantano; piedra crema, dorado y lavanda para ruinas;
azul noche, cian y cobre para torre; obsidiana, carmesí y violeta para fortaleza.
El pantano incluye terreno seco continuo; torre y fortaleza tienen plataformas
sin obstáculos centrales. Son ilustraciones de estética retro, sin imponer una
paleta indexada de consola ni un límite técnico estricto de colores.
