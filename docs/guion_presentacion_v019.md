# Guion de demostración en diez minutos

Objetivo: explicar el problema, los dos métodos del curso y sus resultados,
usando el juego para mostrar decisiones. El tiempo es un presupuesto de ensayo,
no una duración medida ni una promesa de cubrir una partida completa.

| Tiempo acumulado | Pantalla | Qué explicar |
| --- | --- | --- |
| 0:00 a 0:45 | F5, objetivo | Un agente administra recursos y combate para salvar el Mundo Digital. |
| 0:45 a 2:00 | F5, MDP | Diez variables, estado inicial, acciones legales, transiciones, recompensas y terminales. Siete regiones no significan siete estados. |
| 2:00 a 3:20 | F5, métodos | Bellman y modelo conocido en Value Iteration; episodios completos, First-Visit y política ε-greedy en MC. |
| 3:20 a 5:00 | F4, victorias y cobertura | Cinco semillas, 200 evaluaciones por punto y presupuestos acumulativos. MC pasa de 14,9 % a 82,6 %; DP de referencia 96,0 %. |
| 5:00 a 6:00 | F4, cobertura y respaldos | Cobertura final MC 25,7 %; respaldo 0,19 %. No son pruebas de optimalidad ni convergencia formal. |
| 6:00 a 8:00 | F1/F2, partida y T | Mostrar una ruta, una decisión y su inspección. Usar V rápido o Espacio si la presentación de combate consume tiempo. |
| 8:00 a 9:00 | F6 y mapa | Demostrar una habilidad y la digievolución; explicar que audio e imágenes representan el resultado y no entrenan al agente. |
| 9:00 a 10:00 | Conclusión | Responder qué se aprendió, límites del protocolo y evidencia reproducible. Reservar margen para cerrar dentro del máximo. |

Antes de empezar, comprobar la ventana, el audio y los archivos del experimento.
Usar F8 para mantener silencio durante la explicación y activar un efecto solo
si ayuda a la demostración. F5 no cronometra automáticamente esta exposición.

## Respuestas para la defensa

- **¿Por qué es Markov?** El estado incorpora los recursos y condiciones
  persistentes usados por las transiciones. Los turnos y relojes de animación no
  son variables ocultas que cambien las probabilidades del combate.
- **¿Qué significa First-Visit?** Se actualiza una sola vez por episodio cada
  par estado acción, usando su primera aparición cronológica y su retorno.
- **¿Por qué on-policy?** La política ε-greedy que genera los episodios es la
  que se mejora con Q durante el entrenamiento. Evaluar una versión greedy
  congelada no convierte el entrenamiento en un método off-policy.
- **¿DP aprendió en los mismos episodios que MC?** No. DP usa el modelo completo;
  el eje de episodios corresponde al presupuesto MC. La línea DP es una referencia.
- **¿Se demostró convergencia?** No. Se observó mejora empírica en cinco semillas
  y un presupuesto finito, con exploración constante y cobertura parcial.
- **¿La curva es la política del juego?** No. La curva llega a 20.000 por semilla;
  el archivo MC jugable se entrenó por separado durante 60.000 episodios.
- **¿Qué pasa con los 80 turnos?** Es un límite operativo. Los truncamientos se
  registran y se excluyen de las actualizaciones MC; no se inventa un terminal.
- **¿Las animaciones afectan la política?** No. Leen el Step ya resuelto; volumen,
  dibujo, pausa y omisión no añaden muestreos ni recompensas.
- **¿Qué falta para cerrar?** Registrar la aceptación real en Windows, confirmar
  la URL de entrega y revisar el informe final v0.22 y los créditos de los artistas.

Al ensayar, anotar la duración real y reducir la demostración visual si se
excede el máximo. No es necesario esperar a completar una aventura estocástica.
