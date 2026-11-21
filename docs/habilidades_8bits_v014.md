# Habilidades animadas en pixel art v0.14

Esta versión continúa la v0.13 y añade efectos visuales para los diez personajes presentes. Cada habilidad tiene una hoja PNG RGBA transparente de cuatro fotogramas en una cuadrícula 2 × 2. El juego la reproduce sobre una cuadrícula lógica de 64 × 64 con escalado sin suavizado. «8 bits» describe la estética retro; el PNG conserva un canal alfa para superponer el efecto sobre el escenario.

## Controles

- **F6:** abre la galería desde el menú o la partida. Selecciona un personaje con clic o con las flechas.
- **Espacio en la galería:** repite la animación. **F6 o Esc:** vuelve a la pantalla de origen.
- **Espacio durante un combate animado:** termina la animación actual sin ejecutar otra acción. El siguiente Espacio permite continuar como antes.
- **F1, F2, F3, F4, F5 y T:** conservan sus funciones anteriores.

Los ataques del protagonista y los contraataques se presentan por separado. El modo automático espera a que termine la secuencia. Las acciones manuales quedan temporalmente desactivadas durante la reproducción. Ayuda, pausa y paneles conservan el turno y detienen su secuencia visual.

## Referencias y decisiones de diseño

Se consultaron las descripciones del Digimon Reference Book oficial el 4 de noviembre de 2026. Los efectos son recreaciones para este proyecto, no recortes de las ilustraciones de esas páginas. La paleta, las siluetas simplificadas y los cuatro fotogramas son decisiones artísticas. Las denominaciones varían según idioma y adaptación.

| Personaje | Habilidad mostrada | Interpretación visual | Fuente |
|---|---|---|---|
| Agumon | Baby Flame | Bola de fuego pequeña y estela naranja | [Agumon](https://digimon.net/reference_en/detail.php?directory_name=agumon), cuyo perfil inglés la llama Pepper Breath |
| Greymon | Mega Flame | Llamarada amplia y explosión de fuego | [Greymon clásico](https://digimon.net/reference_en/detail.php?directory_name=greymon-first) |
| MetalGreymon | Giga Destroyer | Dos misiles con propulsión y explosión | [MetalGreymon Vaccine](https://digimon.net/reference_en/detail.php?directory_name=metalgreymon-v) |
| WarGreymon | Terra Force | Esfera de energía dorada y estallido radial | [WarGreymon](https://digimon.net/reference_en/detail.php?directory_name=wargreymon) |
| Betamon | Electric Shock | Descarga eléctrica azul y amarilla | [Betamon](https://digimon.net/reference_en/detail.php?directory_name=betamon) |
| Goblimon | Goblin Strike | Proyectil de fuego rojizo veloz | [Goblimon](https://digimon.net/reference_en/detail.php?directory_name=goburimon) |
| Ogremon | Haouken | Puño de energía violeta | [Ogremon](https://digimon.net/reference_en/detail.php?directory_name=orgemon), cuyo perfil inglés la llama Pummel Whack |
| Devimon | Death Claw | Garra oscura y tajos violetas | [Devimon](https://digimon.net/reference_en/detail.php?directory_name=devimon) |
| Andromon | Spiral Sword | Cuchilla giratoria de energía cian | [Andromon](https://digimon.net/reference_en/detail.php?directory_name=andromon) |
| Piedmon | Trump Sword | Cuatro espadas con aparición violeta | [Piedmon](https://digimon.net/reference_en/detail.php?directory_name=piemon) |

Se utiliza la variante clásica naranja de MetalGreymon. La ficha oficial sin sufijo `metalgreymon` corresponde a la versión de 2010, cuyo ataque se describe de otra manera; la referencia empleada es `metalgreymon-v`.

## Archivos y reutilización

Los diez atlas están en `assets/effects/`. Los nombres de archivo corresponden a los identificadores de la tabla, en minúsculas y con guiones bajos. `GENERACION.json` contiene los prompts completos y la procedencia de creación. El orden de los fotogramas es superior izquierdo, superior derecho, inferior izquierdo e inferior derecho. No se recorta cada fotograma por separado: sus márgenes mantienen el anclaje durante la animación.

La vista previa animada está en `resultados/efectos_v014/Vista_Previa_Habilidades_v014.gif`; la galería interactiva permite examinarlos sin compresión GIF.

## Integración con el proyecto académico

`CombatAnimation` interpreta un `Step` ya resuelto. No llama al generador aleatorio, no vuelve a calcular recompensas y no entrena agentes. `EffectSprites` carga y cachea los PNG. Las reglas, costos, daño, precisión, estados y políticas mantienen sus valores.

Si el rival es derrotado no se muestra un contraataque. Las interrupciones confirmadas muestran «INTERRUMPIDO». Cuando no disminuyen los PS se muestra «SIN DAÑO», sin afirmar que hubo un fallo de precisión: podría existir protección. El terminal de derrota no conserva los PS finales del rival, por lo que la presentación evita inventar si el golpe del protagonista acertó en ese caso.

La intensidad visual del contraataque aumenta cuando estaba anunciado como cargado. Los nombres del registro y de la alerta se traducen visualmente a los nombres de las habilidades de esta galería; el controlador y el motor mantienen sus bytes originales.

## Verificación

`VALIDAR_WINDOWS.bat` incluye el diagnóstico de efectos. Puede ejecutarse directamente con `python scripts/validar_efectos_v014.py --headless`. La opción `--gif` requiere Pillow y solo sirve para exportar una vista previa; el juego y los diagnósticos normales no la requieren.

La evidencia incluida se generó en Linux con Pygame y SDL dummy. Se probaron los diez atlas, su transparencia, los fotogramas, la galería, la entrada de usuario y la preservación de estado y RNG. Los escenarios de captura sirven para revisión gráfica y no son nuevos experimentos de aprendizaje. La ejecución nativa en Windows sigue pendiente de realizar en un equipo Windows.
