# v0.22 — Digidex y diario de aventura

La actualización continúa desde **v0.21.1 Guardromon**. Añade dos vistas de consulta y el registro de los turnos; conserva las nueve regiones, catorce conexiones, siete enemigos, cuatro formas protagonistas, efectos, audio y herramientas académicas.

## Uso

| Control | Resultado |
|---|---|
| F7 / botón Digidex | Abre las once fichas con sus sprites actuales. |
| Todos / Formas / Enemigos | Filtra 11, 4 o 7 fichas. |
| Flechas en la Digidex | Cambian de ficha. |
| Fuente oficial | Abre en el navegador la ficha seleccionada de digimon.net. Solo este botón necesita conexión. |
| Tab / botón Diario | Consulta el recorrido de la aventura actual sin gastar turnos. |
| Fin de aventura | Muestra automáticamente el resumen cuando termina la animación del último turno. |
| Anterior / Siguiente o ← / → | Cambian la página de decisiones destacadas del resumen. |
| T · Ver decisión | Abre el laboratorio en el estado **anterior** a la acción indicada. |
| T desde el resumen | Abre el primer momento de la página actual. |
| Esc desde ese laboratorio | Regresa al resumen. |
| Esc desde el diario | Vuelve al juego si está en curso; al menú si terminó. |
| R / Nueva aventura | Reinicia y limpia el registro; se usa la siguiente semilla del controlador. |

La consulta pausa la reproducción del combate y detiene el avance automático. Volver a la partida conserva el estado y el progreso de la animación. El diario conserva únicamente la aventura actual en memoria, hasta reiniciar o cerrar el juego; no es un sistema de partidas guardadas.

## Qué muestra el diario

Se registran los `Step` realmente muestreados por el controlador, junto al origen de la acción: DP, MC, manual o acción de respaldo cuando falta una entrada legal en la política. El historial de mensajes sigue limitado a doce filas; el registro de decisiones conserva todos los turnos de la aventura (máximo habitual: 80).

El resumen muestra resultado, semilla efectiva, modo de control, turnos, combates ganados, formas, ruta, técnicas y pociones usadas, recompensa acumulada y retorno descontado. El retorno se calcula con la γ del laboratorio (0,95 en las políticas incluidas):

`G = r₁ + γ r₂ + γ² r₃ + …`

Un terminal del MDP no conserva todos los recursos. Por eso la salud, energía y poción de una aventura terminal se rotulan **«Antes del turno final»**, usando el último estado observado previo a la acción. En una truncación se conservan y muestran los recursos actuales. El límite de turnos se diferencia de una derrota.

Los momentos destacados son elecciones de ruta, evoluciones, entrenamiento, uso de poción, interrupciones y defensas ante carga. Describen acciones y efectos observables. El laboratorio permite comparar las valoraciones DP y MC del mismo estado; no se infieren motivos internos del agente. Las fichas y el resumen no ejecutan búsquedas, simulaciones ni entrenamiento.

## Canon de Digimon y valores del juego

Las once fichas son Digimon canónicos. Las etiquetas de nivel, tipo, atributo y técnicas de la enciclopedia se conservan en **inglés oficial**; las descripciones breves son resúmenes originales en español. Las estadísticas y técnicas implementadas se muestran aparte, bajo **«En este RPG»**, tomando los valores del modelo existente. Por ejemplo, la ficha inglesa de Agumon indica *Pepper Breath*; el juego conserva el nombre *Baby Flame* de su técnica actual.

Fuentes consultadas el **6 de noviembre de 2026**:

| Digimon | Fuente oficial |
|---|---|
| Agumon | https://digimon.net/reference_en/detail.php?directory_name=agumon |
| Greymon clásico | https://digimon.net/reference_en/detail.php?directory_name=greymon-first |
| MetalGreymon Vaccine | https://digimon.net/reference_en/detail.php?directory_name=metalgreymon-v |
| WarGreymon | https://digimon.net/reference_en/detail.php?directory_name=wargreymon |
| Betamon | https://digimon.net/reference_en/detail.php?directory_name=betamon |
| Goblimon | https://digimon.net/reference_en/detail.php?directory_name=goburimon |
| Ogremon | https://digimon.net/reference_en/detail.php?directory_name=orgemon |
| Devimon | https://digimon.net/reference_en/detail.php?directory_name=devimon |
| Andromon | https://digimon.net/reference_en/detail.php?directory_name=andromon |
| Piedmon | https://digimon.net/reference_en/detail.php?directory_name=piemon |
| Guardromon | https://digimon.net/reference_en/detail.php?directory_name=guardromon |

Los enlaces específicos evitan confundir a Greymon y MetalGreymon clásicos con sus variantes de la serie de 2010. Las fichas están empaquetadas en `src/digimon_rl/data/digidex_v022.json`, por lo que se pueden consultar sin Internet. También se ajustaron los rótulos de ataques enemigos a los nombres de la enciclopedia; se reutilizan sus efectos visuales anteriores sin alterar transiciones, daño ni probabilidad.

## Continuidad académica

Se mantiene `DigitalWorld.RULES_VERSION = v0.21-rutas-y-guardian`: **85.609 estados alcanzables no terminales y dos terminales**. No se reentrenaron políticas ni se modificaron los experimentos.

`resultados/diario_v022/continuidad_v0211.json` registra los SHA-256 de 107 archivos heredados sin cambios: modelo, algoritmos manuales, técnicas, serialización, activos completos, políticas, exportación del laboratorio y curvas actuales de convergencia. `scripts/verificar_continuidad_v022.py` comprueba esos hashes. El ZIP de referencia v0.21.1 tiene SHA-256 `310bdb58dbefdecbabc55dc3091c853a9a4b6d2f2e5e5aff4c0227c9dd7298da`.

Las comparaciones académicas F4/F5 continúan mostrando los experimentos v0.21. Los números de una única aventura del diario son **datos de esa partida**, no nuevas estimaciones de éxito de una política. El Word v0.19 permanece como referencia histórica y requiere integrar los anexos actuales antes de entregar al profesor.

## Validación y aceptación Windows

Se añadieron 16 pruebas centradas en continuidad de las trayectorias, integridad del registro, retorno, recursos terminales, truncación, reinicio, acciones ilegales, respaldo, fichas y navegación. El diagnóstico SDL cubre las once fichas, filtros, enlaces mediante navegador simulado, pausa de animación, diario en curso, victoria DP, victoria MC, derrota manual, límite de turnos, páginas, laboratorio y clics en tres tamaños de ventana.

Ejecutar desde la raíz:

```console
python -m unittest discover -s tests -v
python scripts/validar_digidex_resumen_v022.py --headless
python scripts/verificar_continuidad_v022.py
```

Las capturas de `resultados/diario_v022/interfaz/` son renders del juego con episodios reales. La trayectoria DP de semilla 42 gana en 16 turnos, con recompensa 193 y retorno 105,0405 para γ = 0,95; esta es evidencia de interfaz, no una evaluación estadística adicional.

La evidencia incluida identifica Linux/SDL dummy. **La ejecución del juego en Windows fue confirmada por el usuario**. Esta confirmación manual no incluye un registro de la batería automatizada nativa; los registros incluidos conservan su plataforma Linux/SDL dummy. El ZIP contiene el iniciador para Windows con Python 3.11 o superior y las dependencias declaradas; no contiene un `.exe` autónomo. El primer inicio instala dependencias y requiere Internet. Ejecutar `JUGAR_WINDOWS.bat`, cerrar el juego y ejecutar `VALIDAR_WINDOWS.bat` (16 pasos). Revisar además:

- F7 desde menú y combate: fichas legibles, sprites de la especie correcta y fuente seleccionada correcta.
- Tab durante combate: no avanzar turnos ni perder el progreso de la animación.
- Resumen de victoria/derrota/límite: recursos correctamente rotulados.
- T desde una decisión: estado y acción correspondientes; Esc regresa al resumen.
- F4/F5/F6, audio y pantalla completa conservan su funcionamiento.
- Redimensionar a 1024×768 y 1366×768: botones visibles y clics alineados.
- Guardar los registros de `resultados/validacion_windows/` como evidencia nativa.
