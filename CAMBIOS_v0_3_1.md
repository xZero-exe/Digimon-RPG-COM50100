# Digimon RPG RL — v0.3.1: paquete jugable con gráficos incluidos

**Problema corregido:** v0.3 entregaba un cargador PNG pero las carpetas de arte no incluían imágenes. En una instalación nueva se mostraban los placeholders geométricos.

## Cambios

- Se incluyen **7 sprites pixel-art originales** en `assets/demo/digimon/`: Agumon, Greymon, Betamon, Goblimon, Ogremon, Devimon y Piedmon.
- Se incluyen **6 fondos pixel-art originales** en `assets/demo/backgrounds/`: aldea, bosque, caverna, pantano, ruinas y fortaleza.
- `SpriteManager` carga automáticamente los recursos demo. Si el usuario instala archivos externos **con permiso de sus autores** en `assets/digimon/` o `assets/backgrounds/`, estos reemplazan los recursos demo por nombre.
- Se agrega generador POO-libre de assets `scripts/generate_demo_art.py` (Pillow es opcional; **no hace falta instalarlo para jugar**).
- Se agrega lámina `preview_sprites_v0_3_1.png` que muestra exactamente los sprites incluidos.
- Se agrega una prueba automática que verifica la existencia, tamaño y formato PNG de los trece recursos.
- Se mantiene `import_digidex_sprites.py` para una copia de Digidex que cuente con las autorizaciones correspondientes. No descarga ni incluye recursos de esa fuente.
- Sin cambios en estados, recompensas, transiciones, agentes ni políticas entrenadas.

## Derechos de autor y transparencia

**NO son los sprites de Digidex.** Son ilustraciones fan-made generadas originalmente para este prototipo con primitivas geométricas de Pillow. El repositorio Digidex solicita a quien desee reutilizar sus recursos que pida permisos a los artistas correspondientes; por ello sus PNG no se redistribuyen aquí. Los personajes y nombres de Digimon pertenecen a sus respectivos titulares. El proyecto es educativo, no oficial y no comercial.

## Instalación

```powershell
python -m pip install -e ".[game]"
python -m digimon_rl.play
```

El juego debería indicar `Sprites 7/7` desde la primera ejecución, sin pasos de importación.

> La prueba gráfica en un escritorio Windows sigue pendiente: Pygame no está instalado en el entorno de preparación. Se validan estructura, integridad de PNG, pruebas unitarias y compilación Python.
