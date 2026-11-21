# Modelo MDP v0.8 — Experiencia y habilidades

## Propiedad de Markov

La evolución del mundo cumple `P(s_{t+1},r_t | s_t,a_t, historia)=P(s_{t+1},r_t|s_t,a_t)` porque cada evento probabilístico y sus efectos duraderos se determinan con el estado observable actual: región, HP, energía, HP adversario, evolución, poción, ataque cargado, núcleo, XP y mejora entrenada. No se requieren variables privadas de la interfaz.

El estado `GameState` es inmutable (`dataclass(frozen=True, slots=True)`). Los terminales `Ending.WIN` y `Ending.LOSS` son absorbentes (no hay acciones legales).

## Estados

`s=(L,H,E,V,D,P,C,N,X,M)`, donde:

| Componente | Dominio | Interpretación |
|---|---|---|
| L | 7 zonas | Región del Mundo Digital |
| H | 1..6 | PS de Agumon / digievolución |
| E | 0..6 | Energía |
| V | 0..6 | PS enemigo; 0 = región despejada |
| D | 0..3 | Agumon, Greymon, MetalGreymon, WarGreymon |
| P | 0,1 | Poción disponible |
| C | 0,1 | Enemigo prepara ataque especial |
| N | 0,1 | Núcleo de datos disponible |
| X | 0,1,2 | XP acumulada |
| M | 0,1 | Ataque mejorado permanentemente |

El producto cartesiano tiene `7×6×7×7×4×2×2×2×3×2 + 2 = 395.138` estados nominales; 48.553 no terminales son alcanzables desde el estado inicial según BFS. Es un aumento controlado de los 21.337 estados alcanzables en v0.7.

## Acciones y recompensas nuevas

Después de vencer a un enemigo (excepto el jefe final, que cierra la aventura), el personaje obtiene `min(2,XP+1)` puntos de experiencia. Se mantienen las recompensas previas por vencer, avanzar, recibir daño y terminar la aventura.

En una zona despejada, `Action.TRAIN` es legal solo si `XP=2`, `energía≥1` y `trained=0`. Sus efectos son **deterministas**:

- `XP' = 0`, `E' = E−1`, `trained' = 1`, `reward = −3`.
- Mantiene HP, región, poción, núcleo y forma actual. No avanza de región.
- Durante el resto de la aventura: daño de ataque normal `ATTACK_DAMAGE[D]+1` y especial `SPECIAL_DAMAGE[D]+1`.
- Las probabilidades de acertar ataques siguen siendo 0,90 y 0,75; el entrenamiento aumenta daño, **no** precisión.

Por tanto, la política debe comparar **avanzar directamente** contra **gastar XP/energía y un turno ahora a cambio de ventaja futura**. Este equilibrio se optimiza con `γ=0,95` tanto en Value Iteration como en Monte Carlo.

## Métodos y evaluación

Value Iteration construye el conjunto de estados alcanzables y actualiza `V(s) = max_a Σ_{s',r} P(s',r|s,a)[r+γV(s')]` hasta que la diferencia máxima sea inferior a la tolerancia. El control Monte Carlo first-visit aproxima `Q(s,a)` mediante promedios incrementales de retornos de episodios completos con política ε-greedy on-policy; no calcula expectativas con el modelo.

Se evalúan ambas políticas en las mismas semillas y con igual máximo de 80 acciones por episodio. Los archivos `resultados/validacion_v0_8.json` y `resultados/entrenamiento_v0_8.csv` contienen los valores concretos de esta versión.
