# Versión 0.8.2 — Auditoría de métodos (Cátedra 13)

**Alcance:** mejoras académicas, no se alteran mecánicas del videojuego, el MDP ni sus sprites.

- Monte Carlo **on-policy, first-visit, ε-greedy** con trazabilidad a la Cátedra 13.
- Distingue episodios completos de truncados; solo actualiza Q con retornos terminales completos.
- Registra estados/pares visitados, truncamientos de entrenamiento y cobertura.
- Evalúa la política sin ocultar acciones de respaldo en estados no observados.
- Exporta evaluación multisemilla CSV/JSON y gráfico SVG (solo stdlib de Python).
- Pruebas unitarias específicas para first-visit, truncamientos, fallback y semillas.
- Se conservan los sprites de Digidex **para esta edición local**. No subir imágenes sin permiso de sus autores a GitHub público.
- Políticas DP sin cambios de dinámica; Monte Carlo vuelve a entrenarse con el algoritmo revisado.

Documentación técnica: `docs/auditoria_mc_catedra13_v082.md`.

**Mediciones de entrega:** 90.000 episodios MC (semilla 42), 18.427 estados aprendidos y 42.975 pares estado-acción; validación de 500 partidas: MC 87,4 % y DP 93,6 %; ambos sin respaldos en dicha muestra. Auditoría de 5 semillas con 10.000 episodios cada una: MC 70,47 % de victorias de promedio vs DP 94,20 %; comprobar parámetros antes de comparar porcentajes.
