# Modelo MDP v0.9 – Técnicas por digievolución

**Estado:** s=(L,H,E,V,D,P,C,N,X,M), igual a v0.8.2. No hay nuevas variables: las técnicas producen efectos dentro del turno.

**Acciones:** además de las acciones previas, `Action.TECHNIQUE` está disponible en combate cuando `E >= technique_for(D).energy_cost`. Al elegirla, se consume energía y se evalúa un acierto Bernoulli con la precisión de la técnica.

**Efectos:** daño base + entrenamiento, armadura efectiva `max(0, armor-piercing)` y, cuando procede, cancelación del contraataque cargado si la técnica acierta. Ningún efecto persiste como estado no observado.

**Transición:** `P(s',r|s,a)` se calcula por enumeración exacta en `DigitalWorld.transitions`. `DigitalWorld.sample` genera los episodios. Para cada acción legal las probabilidades suman 1.

**DP (Value Iteration):** `V[k+1](s)=max_a Σ_{s',r} P(s',r|s,a)[r+γ V[k](s')]`. `np.bincount` suma por acción y `np.maximum.reduceat` obtiene el máximo por estado; esta aceleración **no cambia el algoritmo**.

**MC (Cátedra 13):** Q(s,a) se estima mediante promedio de retornos **First-Visit**, política ε-greedy on-policy, sin Exploring Starts. El agente **no consulta el modelo de transición** para realizar expectativas. Los episodios incompletos no actualizan Q.

**Criterio:** superar 15 estados, finitud, observabilidad y episodios terminales. El total nominal incluye combinaciones inalcanzables y no debe confundirse con los 48.553 estados no terminales alcanzables. Los episodios de evaluación tienen tope artificial de 80 turnos; los truncamientos se registran por separado.

**Fuentes:** Cátedra 13 de Monte Carlo Methods III; Sutton y Barto (2018), caps. 4–5; Bertsekas (2017), Vol. I.
