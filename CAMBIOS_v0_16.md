# v0.16 — Combates más expresivos

- Daño, curación y energía flotantes, separados entre acción y contraataque.
- Barras de recursos animadas, destello y desplazamiento local al recibir daño.
- Fases de combate y aviso de intención enemiga con indicaciones legibles.
- V y botón para normal / rápida ×2 / sin animación; Espacio o botón para omitir.
- Pausa de lectura final y congelación de la secuencia al abrir pantallas auxiliares.
- Feedback basado en el turno resuelto, sin segundo muestreo ni cambios al MDP.
- Cobertura de terminales sin inventar PS enemigos perdidos al entrar en derrota.
- Nuevo diagnóstico SDL y séptimo paso de `VALIDAR_WINDOWS.bat`.
- Revisión general de 145/145 pruebas aprobadas y 50 capturas nuevas.

Guía: `docs/combate_v016.md`. Evidencia: `resultados/combate_v016/`.
Se conservan las funciones y los recursos de v0.15. La prueba nativa de Windows
requiere ejecutar el BAT en ese sistema.
