# Corrección de ataques básicos v0.14.1

## Resultado de la revisión

En v0.14, `CombatAnimation.from_step` asignaba un atlas al protagonista únicamente cuando ejecutaba `Action.TECHNIQUE`. Atacar, Ataque especial e Interrumpir recibían `effect=None` y la vista dibujaba tres líneas geométricas. Las cuatro técnicas de digievolución y los seis contraataques enemigos sí utilizaban PNG.

| Acción del protagonista | Estado en v0.14 | Corrección v0.14.1 |
|---|---|---|
| Atacar | Líneas geométricas | Tres tajos de garra blancos con borde ámbar |
| Ataque especial | Líneas geométricas | Doble tajo potenciado dorado y estallido |
| Interrumpir | Líneas geométricas | Corte rápido cian y destello |
| Técnica de cada digievolución | Sprite específico | Se conserva |

Los tres atlas nuevos son `basic_attack.png`, `power_attack.png` e `interrupt_strike.png`, en `assets/effects/`. Cada uno contiene cuatro fotogramas transparentes en una cuadrícula 2 × 2. Sus prompts están en `GENERACION_v0141.json`. Son acciones generales del juego, no nuevas técnicas canónicas de Digimon.

La galería F6 se amplía a 13 efectos y 52 fotogramas. Los tres efectos generales están al final de la lista. Flechas, clic, repetición con Espacio y retorno con F6/Esc mantienen su funcionamiento.

## Cobertura y comprobación

Se comprueba que cada acción ofensiva del protagonista (Atacar, Ataque especial, Técnica e Interrumpir) tenga un atlas disponible en las cuatro formas. El diagnóstico con Pygame renderiza los tres ataques generales en las cuatro formas y visita los 13 elementos de la galería. También valida transparencia, carga de PNG y ausencia de solapamiento entre botones. Sus 61 capturas son escenarios de revisión gráfica, no experimentos nuevos de aprendizaje.

`VALIDAR_WINDOWS.bat` incorpora este diagnóstico. Se puede ejecutar por separado:

```text
python scripts/validar_basicos_v0141.py --headless
```

La vista previa GIF de los tres efectos está en `resultados/basicos_v0141/`. Exportarla con `--gif` requiere Pillow; el juego y el diagnóstico normal no lo requieren.

La evidencia incluida corresponde a Linux con SDL dummy. La ejecución nativa en Windows sigue pendiente.

## Alcance de la corrección

No se alteran reglas, agentes, políticas, estados, daño, costos, precisión ni RNG. Los tres efectos generales se comparten entre las cuatro digievoluciones, que conservan además sus técnicas exclusivas.

Curar, Defender y Digievolucionar mantienen sus efectos geométricos anteriores: son acciones de apoyo, no ataques. Las líneas de emergencia se conservan como respaldo si falta o se corrompe un archivo; con los PNG completos, todas las acciones ofensivas usan sprites.
