# v0.21.1 — Identidad Digimon corregida

El enemigo inventado de v0.21 se elimina y se sustituye por **Guardromon**.
Es un Digimon de tipo Máquina con técnica oficial **Destruction Grenade**:
https://digimon.net/reference_en/detail.php?directory_name=guardromon

El sprite procede del mismo repositorio Digidex que los anteriores:
https://github.com/SergioGranSol/digidex/blob/main/resources/img/sprites/x5/guardromon.png

Se incorpora el PNG real, su procedencia, tamaño y SHA-256 al manifiesto. Los
fondos se conservan. El ataque usa una animación de misiles existente y su nombre
oficial en la intención enemiga y la secuencia visual; ya no se representa como
un corte de cristal. Las capturas de v0.21 que mostraban la criatura retirada se
regeneran con Guardromon.

No cambian el MDP, las probabilidades, los costes, recompensas, estados o
políticas. Continúan 85.609 estados no terminales, dos terminales y las políticas
VI/MC ya calculadas. El identificador técnico de reglas v0.21 se conserva porque
esta es una corrección de representación. No se reentrena ni se atribuyen a
Guardromon estadísticas de combate oficiales: los valores son los del RPG.

Los créditos actuales están en `CREDITOS.md`. Guardromon se identifica
como descarga adicional y no como parte del ZIP originalmente enviado por el usuario.

Validación: **181 pruebas aprobadas, sin omisiones**, más la comprobación de
identidad de los archivos del motor y políticas frente a v0.21. Las capturas
se regeneraron con Pygame 2.6.1 y SDL dummy en Linux.

Para las próximas ampliaciones, comprobar la especie y sus técnicas en la
enciclopedia oficial antes de incorporarlas. Los enemigos deben pertenecer a
Digimon; un nombre nuevo o un diseño inspirado no equivale a un Digimon canónico.

Extraer el ZIP completo en una carpeta nueva y ejecutar `JUGAR_WINDOWS.bat`.
La aceptación nativa de Windows sigue pendiente.
