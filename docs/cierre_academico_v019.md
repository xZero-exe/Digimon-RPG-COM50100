# Preparación de la entrega académica v0.19

Esta versión actualiza el informe y la preparación de la demostración sobre el
juego v0.18. No cambia el MDP, los agentes, las políticas, el audio ni los recursos.

## Pauta consultada

Fuente: `Final_Project.pdf`, profesor Matías Pastene Orellana, una página.
Se contrastó con la planificación de COM50100 y la Cátedra 13. La pauta exige
Python, un MDP finito episódico con al menos 15 estados, comparación de Programación
Dinámica con Monte Carlo y ausencia de bibliotecas de aprendizaje reforzado.

El escrito contiene portada, índice, resumen, estado del arte, metodología,
resultados, discusión, conclusión y referencias. La presentación dura como
máximo diez minutos. El material se entrega mediante un enlace a un repositorio
público de GitHub. La pauta indica 29 de noviembre a las 23:59 como plazo del
proyecto; su página no imprime un año ni define extensión, tipografía o porcentajes
de rúbrica. No se agregan requisitos supuestos.

| Requisito | Evidencia actual | Estado |
| --- | --- | --- |
| Python y POO | `src/digimon_rl/`, clases de motor, agentes, controlador y vista | Implementado |
| MDP finito episódico | 48.553 estados no terminales alcanzables y dos terminales | Verificado por las pruebas |
| DP y MC manuales | `agents.py`, Value Iteration y First-Visit on-policy ε-greedy | Implementado |
| Sin bibliotecas RL | Auditoría AST y revisión de dependencias | Aprobado |
| Nueve partes del informe | `Informe_Final_Digimon_RPG_v019.docx` | Redactadas y verificadas |
| Resultados reproducibles | CSV/JSON v0.11, políticas y protocolo conservados | Incluidos |
| Máximo diez minutos | Guion v0.19 y modo F5 | Ensayo del autor pendiente |
| Repositorio público | Aún no se ha registrado una URL para este proyecto | Pendiente |
| Windows y escucha real | `VALIDAR_WINDOWS.bat`, pruebas físicas en el equipo de destino | Pendiente de registrar |

## Qué se actualizó

Se conserva el borrador v0.13 y se incluye una edición nueva con figuras, la
interfaz actual, descripción de audio y separación de dos protocolos. Las curvas
multisemilla llegan a 20.000 episodios por semilla; la política MC del juego
se entrenó con 60.000 episodios y tiene otra evaluación histórica de 500 partidas.
No se presentan sus tasas como si procedieran del mismo experimento.

La figura del informe usa un eje horizontal lineal con los episodios reales.
Los datos originales y las figuras históricas v0.11 no se alteran. Para el
informe se generan figuras nuevas en `figuras_v019/`. La captura del mapa describe
regiones, no un grafo de solo siete estados. Las ecuaciones siguen siendo objetos
matemáticos editables de Word.

`scripts/verificar_entrega_v019.py` comprueba hashes de fuentes, estadísticas
crudas frente a CSV/JSON, metadatos de las políticas, estructura del escrito,
ecuaciones y figuras. Utiliza Python estándar; no requiere Word, LibreOffice ni
entrenamiento. Está incorporado como décimo paso de `VALIDAR_WINDOWS.bat`.

La revisión general registra 161 pruebas de software aprobadas. La auditoría
documental es una comprobación adicional y no se suma artificialmente al número
de pruebas unitarias. La validación incluida corresponde a Linux con SDL dummy.

## Comprobación en Windows

1. Extraer todo el ZIP en una carpeta nueva y abrir `JUGAR_WINDOWS.bat`.
2. Probar F1, F2 y F3; comprobar clics de rutas y acciones legales.
3. Comprobar redimensionado y F11, incluyendo las opciones de salida y reinicio.
4. Probar F8, F9, F10 y «Probar sonido» con un dispositivo real.
5. Revisar daño, poción, contraataque, interrupción, digievolución y cambio de región.
6. Abrir F4, F5, F6 y T; volver sin perder el estado del episodio.
7. Cerrar el juego y ejecutar `VALIDAR_WINDOWS.bat`.
8. Conservar `resultados/validacion_windows/` y completar el registro siguiente.

| Dato de aceptación | Valor por registrar en el equipo Windows |
| --- | --- |
| Fecha y versión de Windows | Pendiente |
| Versión de Python y resolución | Pendiente |
| Resultado del BAT | Pendiente |
| Revisión visual y clics | Pendiente |
| Escucha y controles de audio | Pendiente |
| Nombre de quien probó | Pendiente |

La aprobación automática no reemplaza la inspección visual y sonora. No se
presenta una ejecución en Linux como certificación de Windows.

## Preparación de GitHub

La preparación de publicación de v0.19 es histórica. La edición pública v0.22 incorpora los sprites de Digidex con sus créditos completos en `CREDITOS.md`, además del código, recursos, políticas, CSV/JSON e informe actualizado. Consultar el README principal para el enlace vigente de entrega.

## Revisión del autor

El documento está preparado para revisión académica. Confirmar el nombre de
portada, explicar las decisiones con comprensión propia y ensayar el guion antes
de entregarlo. Las referencias al programa y cátedras son fuentes del curso;
las capturas y videos son evidencia de software, no mediciones de aprendizaje.

Para editar el informe con el generador se requieren `python-docx` y `matplotlib`.
Estos paquetes solo se necesitan para regenerar el documento, no para jugar ni
ejecutar la comprobación documental. Después de cambiar el texto, revisar de
nuevo su paginación y el índice en Word o con el renderizador de documentos.
