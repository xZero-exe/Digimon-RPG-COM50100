# Cambios — v0.3 (19 de octubre de 2026)

## Recursos visuales

- Nuevo catálogo de Digimon para los seis escenarios y su protagonista: Agumon, Greymon, Betamon, Goblimon, Ogremon, Devimon, Piedmon.
- `SpriteManager` con lectura local opcional de PNG, transparencia, recorte, escala pixel art y caché.
- Seis fondos de escenarios propios generados con código; opción de usar fondos locales con permiso.
- Efectos de presentación básicos para ataque, curación y digievolución (no modifican el modelo RL).
- Nuevos nombres de enemigo en la interfaz; el combate sigue utilizando las mismas probabilidades de la v0.2.
- Contador de recursos visuales instalados en la interfaz.

## Integración

- Nuevo `--assets` en el lanzador para especificar carpeta de recursos.
- Importador que copia desde una **copia local** de Digidex solo tras confirmar permisos; sin descarga ni redistribución automática.
- PNG externos excluidos por `.gitignore`; no se empaquetan sprites ajenos.
- Guía de instalación, créditos y restricciones de uso.

## Compatibilidad RL / pruebas

- `DigitalWorld`, `GameState`, `ValueIterationAgent` y `MonteCarloAgent` no se han modificado.
- Se mantienen las políticas DP y MC guardadas de v0.2; no requieren reentrenamiento.
- 22 pruebas unitarias aprobadas, frente a las 16 anteriores.
- La interfaz se ha comprobado sintácticamente, pero falta prueba gráfica real porque Pygame no se pudo instalar en este entorno sin acceso a la red.
