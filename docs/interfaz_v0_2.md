# Interfaz gráfica v0.2 — Integración con el MDP

## Objetivo

Visualizar decisiones de políticas preentrenadas, sin cambiar las funciones matemáticas del entorno.

## Flujo por turno

1. `RPGApp` lee teclado o ratón y solicita avanzar a `AdventureController`.
2. Si el modo es automático, `AdventureController.selected_action()` obtiene la acción guardada en la política DP o MC; si el modo es manual, el usuario elige una acción legal.
3. `DigitalWorld.actions(state)` determina las acciones válidas y `DigitalWorld.transitions(state, action)` define la distribución de transiciones y recompensas.
4. `DigitalWorld.sample(outcomes, rng)` sortea el resultado; **se usa la misma implementación que en entrenamiento y evaluación**.
5. `AdventureController` actualiza el estado, recompensa y log. `RPGApp.draw()` renderiza esa información sin escribir reglas de combate.

```text
[Controles] → [RPGApp] → [AdventureController] → [DigitalWorld]
                       ↘ [Políticas DP/MC guardadas] ↗
```

## Responsabilidades POO

| Elemento | Responsabilidad |
|---|---|
| `DigitalWorld` | Reglas físicas/matemáticas del MDP, acciones y transiciones |
| `ValueIterationAgent` | Bellman optimality para determinar política sobre estados alcanzables |
| `MonteCarloAgent` | Control first-visit episódico epsilon-greedy; sin cálculo de expectativas de modelo |
| `AdventureController` | Avance paso a paso, modos, episodios y registro de sucesos |
| `RPGApp` | Dibujar mapa, escena de combate y botones; capturar comandos |
| `policy_io` | Exportar/importar pares estado-acción en JSON |

## Por qué se guardan las políticas

Pygame no inicia reentrenando. Las políticas se serializan con los componentes explícitos del estado, la acción y metadatos (algoritmo, gamma, semilla y número de episodios MC). Se valida la legalidad de las acciones en la carga. Después de modificar el MDP, se deben regenerar ambas políticas.

## Validación

- Unit tests: modelo, políticas, persistencia JSON y controlador de sesiones.
- Las ejecuciones sin Pygame comprueban la consistencia de las probabilidades, acciones legales y simulaciones.
- No se pudo realizar smoke test visual de Pygame dentro de este entorno de construcción al no estar disponible esa dependencia; debe verificarse en una máquina que sí la tenga instalada.

## Limitación explícita

El escenario de la interfaz representa la **zona actual** del MDP. No existe un sistema de coordenadas de personaje dentro de cada región; implementarlo como movimiento libre alteraría los estados y requeriría rehacer el modelo y las políticas. La navegación entre zonas sí está gobernada por el MDP existente.
