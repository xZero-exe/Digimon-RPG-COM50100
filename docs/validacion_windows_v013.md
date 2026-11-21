# Validación de Digimon RPG v0.13 en Windows

## Estado de la evidencia incluida

La generación de esta versión se realizó en **Linux con Python 3.12 y Pygame 2.6.1**, utilizando el controlador de vídeo SDL `dummy`. Se renderizaron las pantallas reales, se verificaron botones y coordenadas y se ejecutaron partidas DP y MC completas. Las capturas y el registro están en `resultados/interfaz_v013/`.

**La ejecución nativa en Windows está pendiente.** Ni el controlador dummy ni la revisión estática de los BAT sustituyen esa prueba. El paquete incluye el código fuente ejecutable y un iniciador BAT; requiere Python 3.11 o superior y acceso a Internet para instalar las dependencias la primera vez. No es un EXE autónomo.

## Instalación y prueba automática

1. Extrae **todo** el ZIP en una carpeta nueva. Puedes usar una ruta con espacios.
2. Ejecuta `JUGAR_WINDOWS.bat`. El iniciador comprueba los archivos, crea `.venv`, instala las dependencias necesarias y abre el juego.
3. Cierra el juego y ejecuta `VALIDAR_WINDOWS.bat`.
4. Espera a que finalicen las pruebas y las aperturas breves de ventanas. El proceso genera `resultados/validacion_windows/`, con registros, capturas y un JSON que identifica el sistema operativo real. Un código de salida distinto de cero indica que alguna comprobación falló.
5. Conserva esos archivos como evidencia de la máquina usada. El script puede cambiar brevemente a pantalla completa; no envíes clics mientras recorre las pantallas.

El diagnóstico prueba las seis diapositivas, cuatro métricas, cuatro formas, siete acciones manuales, laboratorio, teclado, retorno de paneles, clics en cuatro resoluciones y dos aventuras completas. Algunos estados se construyen exclusivamente para revisar la presentación; las capturas **no son resultados de experimentos de aprendizaje**.

## Revisión humana de aceptación

| Comprobación | Resultado esperado | Estado en Windows |
|---|---|---|
| Inicio desde carpeta extraída | Abre sin traceback | Pendiente |
| Equipo de 1366 × 768 | Ventana inicial completa, sin cortar botones inferiores | Pendiente |
| Redimensionar ventana | Conserva proporciones y clics sobre los botones | Pendiente |
| F11 y F11 nuevamente | Entra y sale de pantalla completa y recupera tamaño anterior | Pendiente |
| F1 y F2, Espacio, A, + y − | Avanza, reproduce, pausa y cambia velocidad | Pendiente |
| F3 y acciones 1–7 | Cada tecla y cada botón eligen la acción correspondiente | Pendiente |
| Combate con siete acciones | Dos filas legibles sin superposición | Pendiente |
| F4, flechas y clic en métricas | Cuatro gráficos con etiquetas legibles | Pendiente |
| F5 y flechas | Seis páginas y acceso a partidas | Pendiente |
| T y volver | Muestra Q y conserva el estado de la aventura | Pendiente |
| H, P, M y R | Ayuda, pausa, menú y reinicio correctos | Pendiente |
| Cerrar con X | Cierre limpio, sin procesos del juego pendientes | Pendiente |

Además de resolución, registra versión de Windows, Python, Pygame, escala de pantalla (100/125/150 %), resultado visual y cualquier error. Para repetir la prueba técnica sin abrir ventanas: `.venv\Scripts\python.exe scripts\validar_interfaz_v013.py --headless`. Ese modo no cierra la aceptación visual.
