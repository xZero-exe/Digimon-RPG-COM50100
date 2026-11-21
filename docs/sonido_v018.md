# Sonido y transiciones — v0.18

Continuación de v0.17. Se conservan los siete fondos, el mapa ilustrado, los trece
efectos gráficos, el feedback de combate y las pantallas F4, F5, F6 y T.

## Efectos originales

Se incluyen **23 WAV**: los trece ataques, botones, poción, defensa, digievolución,
impacto, resultado sin daño, interrupción, viaje, victoria y derrota. Son efectos
cortos de estilo retro sintetizados con ondas, barridos y ruido determinista.
No se usan muestras, música ni melodías de otros videojuegos. Esta versión
incorpora efectos, sin una pista musical continua.

El código de generación está en `scripts/generar_sonidos_v018.py`. Los WAV son
mono, PCM de 16 bits a 22.050 Hz, con picos limitados a 0,72 antes del volumen del
jugador. Sus duraciones y hashes están en `assets/audio/manifest_v018.json`.
Los archivos se incluyen en el ZIP; el juego no descarga sonidos ni los genera
durante la partida. Se utiliza el mezclador de Pygame, sin dependencias nuevas.

## Controles

| Control | Función |
| --- | --- |
| F8 / botón «Sonido» | Silenciar o activar los efectos |
| F9 / botón − | Reducir el volumen en diez puntos porcentuales |
| F10 / botón + | Aumentar el volumen en diez puntos porcentuales |
| «Probar sonido» | Reproducir una muestra con el volumen seleccionado |
| F6 → «Escuchar efecto» | Escuchar una vez la habilidad seleccionada |
| V | Mantener las opciones normal, rápida ×2 y sin animación |
| Espacio / «Omitir animación» | Omitir tanto el combate como el viaje actual |

Los controles de audio están disponibles en el menú, la partida y las pantallas
auxiliares. El volumen inicial es 35 %. Volumen y silencio se guardan por usuario:
en Windows, `%APPDATA%/Digimon_RPG_RL/audio.json`; en Linux, la carpeta de
configuración del usuario. Si no se puede guardar, la preferencia sigue funcionando
en esa sesión. Un archivo de configuración inválido recupera valores predeterminados.

La galería no reproduce sonido en bucle: escuchar es una acción optativa.
Ni los controles ni la escucha consumen turnos o números aleatorios del MDP.

## Sincronización y viajes

Las señales sonoras se programan a partir del turno que ya resolvió el motor.
Cada ataque tiene su efecto; los impactos se sincronizan con el cambio visual de
PS. «Sin daño» utiliza una señal neutra, sin afirmar un acierto. Un contraataque
cancelado no produce el sonido de ataque enemigo. La victoria o derrota suenan
una sola vez al terminar su presentación; el límite de turnos no se confunde con
una derrota por falta de PS.

Al abrir pausa, resultados, presentación o laboratorio, el reloj visual y los
canales del combate quedan pausados. El audio de los botones sigue disponible.
Al volver, la secuencia continúa; el juego no acumula sonidos por cada redibujado.
Si un frame se retrasa mucho, se descartan señales antiguas para evitar una ráfaga.
Silenciar no almacena sonidos para reproducirlos después de activar el audio.

Los cambios de región tienen un fundido oscuro de **560 ms** que conserva el
aspecto de ambos escenarios y anuncia el destino. Una emboscada muestra su
pérdida real de PS al llegar. El controlador ya resolvió un único paso: el fundido
no añade otro estado del MDP, otra transición aleatoria ni otra recompensa.
Las acciones manuales y el automático esperan su final. La velocidad rápida
reduce su duración a la mitad; sin animación se muestra el destino inmediatamente.

Omitir cancela sonidos pendientes y no juega otro turno. Con V «sin animación»,
un turno nuevo conserva un sonido resumido de su acción; el silencio se controla
independientemente con F8. Los avisos narrativos esperan a que termine el viaje.

Si no hay dispositivo o el mezclador deja de estar disponible, el juego continúa
sin audio y muestra «Audio no disponible». Un WAV faltante tampoco interrumpe
la partida. El indicador no certifica que los altavoces estén conectados o que
el volumen del sistema operativo permita escuchar: «Probar sonido» sirve para
la comprobación manual.

## Validación y Windows

Resultado de esta entrega: **161/161 pruebas aprobadas**, auditoría estática sin
bibliotecas RL, los **23 WAV** cargados con el mezclador SDL y **22 capturas** del
nuevo diagnóstico. Se prueban preferencias, silencio, sincronización, pausas,
omisión, galería optativa, ausencia de dispositivo y cierre del mezclador.
Los archivos del motor, políticas, reglas del mapa, feedback de combate, recursos
anteriores y resultados académicos se comparan con v0.17 y permanecen idénticos.

La evidencia corresponde a **Linux con video/audio SDL dummy**. Comprueba la
ejecución nativa y la escucha en Windows extrayendo todo el ZIP, abriendo
`JUGAR_WINDOWS.bat` y usando «Probar sonido». Luego cierra el juego y ejecuta
`VALIDAR_WINDOWS.bat`: sonido y viajes son su noveno paso. Si no hay dispositivo,
el diagnóstico informa la ruta de respaldo; no certifica una escucha física.

El video `resultados/audio_v018/Vista_Previa_Sonido_v018.mp4` es un montaje de
escenarios legales de revisión, con el render real y los mismos WAV del juego.
El audio se compone para exportación a partir de los eventos del reproductor;
no es una grabación del dispositivo ni un experimento nuevo de aprendizaje.
Sus eventos están en `eventos_video_v018.json`.

Para regenerarlo opcionalmente: `python scripts/validar_audio_v018.py --headless --video`.
**FFmpeg solo se requiere para esa exportación**, no para jugar ni para la
validación normal. No hay algoritmos de aprendizaje nuevos ni cambios a DP/MC.
