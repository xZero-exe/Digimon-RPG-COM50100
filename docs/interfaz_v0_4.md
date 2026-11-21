# Interfaz del RPG v0.4 — Guía de usuario

## Inicio

Al abrir `JUGAR_WINDOWS.bat` aparece un menú con los tres modos:

- **F1 / Programación Dinámica:** visualiza las decisiones calculadas por Value Iteration.
- **F2 / Monte Carlo:** visualiza decisiones de la política aprendida a partir de episodios.
- **F3 / Manual:** el jugador selecciona una de las acciones válidas en cada estado.

El agente no se entrena durante la partida: las políticas JSON ya están guardadas en `politicas/`. El entorno continúa usando las transiciones probabilísticas originales.

## Controles

| Tecla | Acción |
|---|---|
| F1, F2, F3 | Comenzar/cambiar de modo. Cambiar de modo reinicia el episodio. |
| Espacio o Enter | Cerrar aviso narrativo o avanzar un turno del agente. |
| A | Reproducción automática / pausa de reproducción (DP y MC). |
| 1 a 5 | Elegir acción legal (modo manual). |
| + / - | Cambiar velocidad de reproducción automática. |
| R | Reiniciar aventura con el modo actual. |
| P | Pausar la aventura / regresar. |
| H | Mostrar ayuda. |
| C | Mostrar créditos. |
| M o Escape | Regresar al menú principal (desde la partida). |
| Ratón | Elegir botones y acciones legales. |

Durante la selección inicial, **Enter** empieza el modo resaltado y **Escape** cierra el programa.

## Avisos y combate

Los mensajes de historia se generan a partir de cambios de estado ya calculados, como alcanzar otra zona o evolucionar. **No representan acciones del agente** ni alteran el MDP. Durante la reproducción automática se espera a que desaparezca el mensaje de región. En combate, se muestran barras de PS, la acción y la recompensa del último turno (información real del motor).

## Prueba local

Ejecuta `JUGAR_WINDOWS.bat` desde una carpeta extraída del ZIP. Si es la primera vez, necesita Internet para instalar Pygame (si no está disponible en el sistema). La ventana usa una resolución lógica de **1280 × 820**, por lo que se recomienda una pantalla con suficiente espacio.

La edición pública incorpora los sprites de `assets/digimon/` y reconoce a los creadores de Digidex en `CREDITOS.md`.
