# Combates más expresivos — v0.16

Continuación directa de v0.15. Se conservan los siete fondos, los trece efectos,
los sprites, el mapa y las pantallas académicas. El cambio se concentra en la
presentación de los turnos que el controlador ya resolvió.

## Cambios visibles

- Cifras flotantes de daño y curación en PS, y de gasto/recuperación de energía.
- Barras de vida y energía con interpolación y una estela del recurso anterior.
- Destello breve del personaje que recibe daño o curación; leve desplazamiento
  local al impacto, sin mover la pantalla ni consumir números aleatorios.
- Etiquetas separadas para **Tu acción**, **Contraataque**, **Interrumpido** y
  **Resultado**. Los ataques cancelados no muestran un proyectil enemigo.
- Aviso de ataque cargado con una sugerencia de defensa o interrupción, según
  los recursos disponibles. Es una ayuda visual, no una acción automática.
- Pequeña pausa de lectura al terminar el turno; los agentes automáticos esperan
  a que termine la secuencia antes de avanzar.

## Controles

| Control | Función |
| --- | --- |
| V / botón «Animación» | Alternar normal, rápida ×2 y sin animación |
| Espacio durante la animación | Terminar su presentación sin ejecutar otro turno |
| Botón «Omitir animación» | La misma acción de omisión, disponible durante el combate |
| + / − | Ajustar la espera entre decisiones del modo automático |
| P / F4 / F5 / F6 / T | Abrir las pantallas existentes; la animación queda detenida |

La preferencia de velocidad se conserva al reiniciar aventuras dentro de la misma
sesión. No se guarda al cerrar el programa. Con «sin animación» se aplica el
resultado inmediatamente; las reglas y el muestreo son exactamente los mismos.

## Cifras fieles al modelo

Se muestra la pérdida efectiva de PS, limitada por la vida que tenía el objetivo.
Un ataque que derrota a un enemigo con 1 PS muestra −1 PS, aunque su daño nominal
fuera mayor. Una poción muestra solo la vida que realmente puede restaurar hasta
el máximo de 6. Si después golpea el enemigo, se muestra ese daño por separado.

Ejemplo: con 2 PS, una poción restaura 3 PS y un contraataque cargado quita 3 PS.
La secuencia muestra **2 → 5 → 2**, con **+3 PS** y **−3 PS**; no confunde un
balance neto nulo con una poción inútil.

«Sin daño» no afirma necesariamente un fallo: la armadura puede absorber un golpe.
En una interrupción, que ignora armadura, cero daño permite mostrar «Falló».
Los terminales de derrota del MDP descartan los PS enemigos. En ese caso no se
inventa un número: se usa **?** y una barra rayada para ese dato, manteniendo
correctamente la vida final del héroe en 0. La energía terminal se presenta con
los costos deterministas de la acción y las constantes compartidas del motor.

No se modifica `Step`, el espacio de estados, los daños, las probabilidades,
las recompensas, las acciones legales ni las políticas. Las clases
`TurnFeedback`, `VitalChange`, `VitalFrame` y `FloatingNotice` son datos de
presentación; no implementan un método de aprendizaje ni resuelven transiciones.

## Validación

Resultado de la revisión general: **145/145 pruebas aprobadas**, auditoría estática
de 66 archivos Python sin bibliotecas de RL y **50 capturas SDL** del nuevo
diagnóstico. Se incluyen el registro completo y la comprobación de conservación
del motor, políticas, recursos y resultados académicos frente a v0.15.

`tests/test_combat_feedback_v016.py` compara el resultado final de las barras con
los resultados legales del motor en diferentes regiones, formas, niveles de vida
e intenciones. Revisa también límites de curación, daño efectivo, armadura,
interrupción, terminales, interpolación y digievolución durante la pausa de lectura.

`scripts/validar_combate_v016.py` ejecuta Pygame real con once casos de combate,
capturas de ambas fases y pruebas de teclado/clic, pausa, bloqueo de un segundo
turno, omisión y modo instantáneo. Comprueba que dibujar no modifica el estado,
la recompensa ni el RNG, que los botones no se superponen y que los textos
permanecen dentro de la ventana. `--gif` añade una vista previa (requiere Pillow).

En Windows: extraer todo el ZIP, abrir `JUGAR_WINDOWS.bat`, cerrar el juego y
ejecutar `VALIDAR_WINDOWS.bat`. El nuevo diagnóstico es su séptimo paso.
La evidencia incluida se obtuvo en **Linux con SDL dummy**; la ejecución nativa
en Windows continúa pendiente de esa comprobación en un equipo Windows.

Revisión visual sugerida: usar una poción en combate, defender un golpe cargado,
intentar una interrupción y cambiar la velocidad con V. Comprobar que Espacio
omite la presentación y que hace falta otra decisión para jugar un nuevo turno.
