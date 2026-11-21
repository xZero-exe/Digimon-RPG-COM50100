# v0.14 — Habilidades animadas en pixel art

Continuación completa de v0.13, con los sprites de personajes y funciones anteriores.

- Diez atlas PNG transparentes, con cuatro fotogramas cada uno: cuatro técnicas del protagonista y seis habilidades enemigas.
- Recreaciones gráficas basadas en las descripciones del Digimon Reference Book; referencias y prompts completos incluidos.
- F6 abre una galería con selección de los diez personajes, animación repetible y vista de los cuatro fotogramas.
- Secuencia visual de acción y contraataque, coordinada con el turno ya resuelto.
- Se distinguen golpe final, contraataque cancelado y ausencia de daño.
- Espacio permite terminar la animación sin consumir otro turno. El modo automático espera al final de la secuencia.
- Diagnóstico SDL de efectos, 50 capturas y vista previa GIF. Nuevas pruebas de integridad visual y de interpretación de resultados.

No se modifican `environment.py`, `agents.py`, `domain.py`, `session.py`, `techniques.py` ni las políticas. No se añaden algoritmos ni bibliotecas de aprendizaje reforzado.

El informe preliminar v0.13 se conserva como documento de la etapa anterior. El detalle visual nuevo está en `docs/habilidades_8bits_v014.md`.

La evidencia automática identifica Linux/SDL dummy; la prueba nativa en Windows está pendiente. `VALIDAR_WINDOWS.bat` ejecuta también el nuevo diagnóstico gráfico.

## Evidencia de esta entrega

132/132 pruebas aprobadas. Auditoría de 58 archivos Python sin importaciones conocidas de librerías RL. Diagnóstico de efectos aprobado con 50 capturas, 40 fotogramas, transparencia y navegación sin consumo adicional de estado o RNG.
