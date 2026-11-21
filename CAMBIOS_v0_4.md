# Digimon RPG — Cambios v0.4

## Pantalla principal y experiencia RPG

- Pantalla de inicio con tres modos seleccionables: **Value Iteration**, **Monte Carlo** y **manual**.
- Ayuda en pantalla, créditos de recursos visuales y opción de pausa.
- Historias cortas al llegar a cada una de las seis zonas, al digievolucionar y al vencer enemigos.
- Iconos de Digimon en los nodos del mapa, manteniendo la estructura del MDP.
- Barra de salud sobre el enemigo durante el combate.
- Mensaje temporal tras cada turno con la acción y la recompensa efectivamente devuelta por `DigitalWorld`.
- Los avisos se pueden cerrar manualmente y se cierran solos; la reproducción automática espera a que desaparezcan para facilitar la lectura.

## Estructura POO

- Nueva clase `GamePresentation`: estados de pantalla (`Screen`) y avisos (`StoryBeat`), sin Pygame ni lógica de combate.
- Clase `RPGApp` ampliada para gestionar escenas, entrada y renderizado. Toda la lógica de aprendizaje sigue fuera de la vista.
- `DigitalWorld`, `GameState`, `AdventureController`, `ValueIterationAgent` y `MonteCarloAgent` no se modificaron.
- Políticas JSON incluidas y compatibles con v0.3.2.

## Pruebas

- **37 pruebas automatizadas aprobadas** en el entorno de desarrollo.
- Incluye pruebas sin Pygame que simulan eventos de teclado, navegación de pantallas y cambios de modo.
- Se comprobó que los PNG de Digidex del ZIP siguen íntegros mediante SHA-256.
- **Pendiente**: abrir y revisar la ventana de Pygame en Windows. En el entorno de construcción no fue posible instalar la biblioteca por una restricción de conexión.

## Derechos de los sprites

Los 7 PNG de Digidex provienen del ZIP compartido por el usuario. Esta compilación está destinada a **uso local de prueba**. La licencia MIT del código del repositorio Digidex no equivale a una autorización para republicar las ilustraciones de terceros. `assets/digimon/*.png` está excluido por `.gitignore`. Antes de publicar una versión en GitHub, verificar autorizaciones y créditos por artista.
