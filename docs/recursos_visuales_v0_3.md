> **Actualización v0.3.2 (paquete personal):** esta entrega ya incluye los siete PNG x5 de Digidex aportados por el usuario en `assets/digimon/`. No hace falta ejecutar el importador ni descargar los PNG por separado. Las secciones anteriores de v0.3.1 se conservan como historia de la implementación; sus afirmaciones de «no se incluyen los sprites de Digidex» **no se aplican a v0.3.2**. La edición pública actual conserva esos recursos y sus créditos en `CREDITOS.md`.

# Digimon RPG RL — Recursos visuales v0.3.1

## Objetivo

En la versión **0.3.1** el juego ya viene con **7 sprites y 6 fondos PNG originales incluidos** en `assets/demo/`, por lo que ya no aparece el dibujo geométrico en una instalación nueva. Los PNG obtenidos de terceros, cuando su autor los autorice, pueden colocarse en `assets/digimon/` o `assets/backgrounds/` para sustituir los de demostración. El motor de aprendizaje reforzado, sus probabilidades, recompensas, estados y políticas **no han cambiado**.

La publicación académica fue confirmada por el responsable del proyecto el 21 de noviembre de 2026; los artistas conservan sus derechos. La licencia MIT de la aplicación Digidex es una licencia de *software* y no garantiza derechos sobre las imágenes de terceros.

## Fuente y atribución

Repositorio examinado: [SergioGranSol/digidex](https://github.com/SergioGranSol/digidex). Su README indica que hay diversos artistas, que autorizan mostrar su arte en **esa página**, y solicita pedir permiso antes de reutilizar sprites y enlazar el contenido y a los creadores.

En v0.3.1 se utilizaban los PNG de demostración de `scripts/generate_demo_art.py`. La edición actual incorpora once PNG de Digidex, documentados en `assets/DIGIDEX_MANIFEST.json` y `CREDITOS.md`.

## Archivos de personajes

En la copia de Digidex hay versiones `x1`, `x2` y `x5`. Se recomienda `x5` para ventanas grandes. Todas estas rutas están verificadas en la rama `main` del repositorio:

| Personaje | Archivo en Digidex | Nombre local | Uso en juego |
|---|---|---|---|
| Agumon | `resources/img/sprites/x5/agumon.png` | `assets/digimon/agumon.png` | Protagonista |
| Greymon | `resources/img/sprites/x5/greymon.png` | `assets/digimon/greymon.png` | Digievolución |
| Betamon | `resources/img/sprites/x5/betamon.png` | `assets/digimon/betamon.png` | Bosque |
| Goblimon | `resources/img/sprites/x5/goblimon.png` | `assets/digimon/goblimon.png` | Caverna |
| Ogremon | `resources/img/sprites/x5/ogremon.png` | `assets/digimon/ogremon.png` | Pantano |
| Devimon | `resources/img/sprites/x5/devimon.png` | `assets/digimon/devimon.png` | Ruinas |
| Piedmon | `resources/img/sprites/x5/piedmon.png` | `assets/digimon/piedmon.png` | Fortaleza |

## Importador opcional (referencia histórica)

1. Consulta `CREDITOS.md` y el manifiesto de los sprites incorporados.
2. Obtén una copia local de Digidex, por ejemplo `git clone https://github.com/SergioGranSol/digidex.git C:\arte\digidex`.
3. Desde la raíz de **nuestro** proyecto, con la copia ya disponible y las autorizaciones confirmadas, ejecuta:

   ```powershell
   python scripts/import_digidex_sprites.py --source "C:\arte\digidex" --scale x5 --i-have-permission
   ```

4. Abre el juego: `python -m digimon_rl.play`. El contador de la arena debe mostrar `Sprites 7/7` incluso antes de esta importación (los siete sprites demo ya están incluidos).

Para reemplazos futuros, conserva la atribución y procedencia de las imágenes en `assets/digimon/`. Las especies sin PNG externo usarán automáticamente los sprites originales que ya vienen en `assets/demo/digimon/`.

Los PNG de `assets/digimon/` forman parte de la entrega pública actual y ya no se excluyen en `.gitignore`. No se recomienda cambiar las reglas del MDP para incorporar más especies: la identidad visual del enemigo depende de la región existente.

## Fondos por zona

Por defecto se cargan seis fondos PNG originales desde `assets/demo/backgrounds/`, uno por región: Aldea, Bosque, Caverna, Pantano, Ruinas y Fortaleza. Opcionalmente se pueden usar imágenes propias o autorizadas:

```text
assets/backgrounds/village.png
assets/backgrounds/forest.png
assets/backgrounds/cave.png
assets/backgrounds/swamp.png
assets/backgrounds/ruins.png
assets/backgrounds/fortress.png
```

## Arquitectura

- `assets_catalog.py`: especies y rutas; sin depender de Pygame.
- `gui/sprites.py` (`SpriteManager`): carga primero imágenes autorizadas en `assets/digimon/` y luego recursos incorporados en `assets/demo/digimon/`, recorta márgenes transparentes, escala por vecino más cercano, refleja enemigos y cachea recursos.
- `gui/app.py` (`RPGApp`): representa los Digimon, pinta fondos locales o procedurales, muestra efectos visuales de ataque, curación y evolución.
- `session.py` (`AdventureController`): conserva el control de turnos y consulta `DigitalWorld`.
- `environment.py` (`DigitalWorld`): **no cambia**; sigue siendo la única fuente de transiciones probabilísticas y recompensas.

Si ejecutas la app desde otra carpeta, puedes especificar:

```powershell
python -m digimon_rl.play --assets "C:\mi-carpeta\assets" --policies "C:\mi-proyecto\politicas"
```

## Cómo verificar

```powershell
python -m unittest discover -s tests -v
```

Las pruebas unitarias comprueban el MDP, los algoritmos, la sesión, el catálogo, la integridad de los PNG incluidos y la importación local. **La ventana Pygame requiere validación visual en Windows**, pues no fue posible instalar Pygame en el entorno donde se preparó esta entrega. Los tests del gestor Pygame no pueden ejecutarse sin esa dependencia.
