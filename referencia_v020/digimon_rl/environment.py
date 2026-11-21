"""Motor del MDP: acciones legales, transiciones probabilísticas y episodios.

No hay estados ocultos: los resultados del turno dependen únicamente de
(state, action). `transitions` es LA fuente de verdad para DP y para simulación.
"""
from __future__ import annotations

from collections import deque
from dataclasses import replace
from random import Random
from typing import Callable

from .domain import Action, Ending, Episode, GameState, State, Step, Transition, Zone
from .techniques import technique_for


class DigitalWorld:
    RULES_VERSION = "v0.20-balance-piedmon"
    DAMAGE_REDUCTION = (0, 0, 1, 2)
    MAX_HP = 6
    MAX_ENERGY = 6
    MAX_ENEMY_HP = 9
    MAX_XP = 2
    TRAINING_COST = 2  # puntos de experiencia
    TRAINING_ENERGY_COST = 1

    ENEMY_HP = {
        Zone.FOREST: 2,
        Zone.CAVE: 3,
        Zone.SWAMP: 3,
        Zone.RUINS: 4,
        Zone.TOWER: 5,
        Zone.FORTRESS: 9,
    }
    ENEMY_HIT_PROB = {
        Zone.FOREST: 0.65,
        Zone.CAVE: 0.75,
        Zone.SWAMP: 0.72,
        Zone.RUINS: 0.80,
        Zone.TOWER: 0.84,
        Zone.FORTRESS: 0.86,
    }
    # Probabilidad de preparar un ataque fuerte tras cada turno enemigo.
    CHARGE_PROB = {
        Zone.FOREST: 0.12, Zone.CAVE: 0.28, Zone.SWAMP: 0.30,
        Zone.RUINS: 0.40, Zone.TOWER: 0.46, Zone.FORTRESS: 0.52,
    }
    ENEMY_DAMAGE = {
        Zone.FOREST: 1,
        Zone.CAVE: 2,
        Zone.SWAMP: 1,
        Zone.RUINS: 2,
        Zone.TOWER: 2,
        Zone.FORTRESS: 3,
    }

    # Digievolución secuencial; es una decisión estratégica, no automática.
    FORM_NAMES = ("Agumon", "Greymon", "MetalGreymon", "WarGreymon")
    # WarGreymon cuesta 2 EN: todavía consume un turno y exige la fortaleza.
    EVOLUTION_COST = (0, 2, 2, 2)
    EVOLUTION_ZONE = (Zone.VILLAGE, Zone.FOREST, Zone.RUINS, Zone.FORTRESS)
    ATTACK_DAMAGE = (1, 2, 3, 5)
    SPECIAL_DAMAGE = (2, 3, 4, 6)

    def start_state(self) -> GameState:
        return GameState(Zone.VILLAGE, hp=6, energy=3, enemy_hp=0, evolved=0, potion=True)

    def can_digivolve(self, state: GameState) -> bool:
        next_form = int(state.evolved) + 1
        return (state.enemy_hp > 0 and next_form < len(self.FORM_NAMES)
                and state.zone.value >= self.EVOLUTION_ZONE[next_form].value
                and state.energy >= self.EVOLUTION_COST[next_form])

    def total_nominal_states(self) -> int:
        """Incluye combinaciones no necesariamente alcanzables + 2 terminales."""
        return (len(Zone) * self.MAX_HP * (self.MAX_ENERGY + 1)
                * (self.MAX_ENEMY_HP + 1) * len(self.FORM_NAMES) * 2 * 2 * 2
                * (self.MAX_XP + 1) * 2 + len(Ending))

    def actions(self, state: State) -> tuple[Action, ...]:
        if isinstance(state, Ending):
            return ()
        if state.enemy_hp > 0:
            result = [Action.ATTACK]
            if state.energy > 0:
                result.append(Action.POWER_ATTACK)
            if state.energy >= technique_for(int(state.evolved)).energy_cost:
                result.append(Action.TECHNIQUE)
            result.append(Action.GUARD)
            if state.potion and state.hp < self.MAX_HP:
                result.append(Action.HEAL)
            if self.can_digivolve(state):
                result.append(Action.DIGIVOLVE)
            if state.enemy_charging and state.energy > 0:
                result.append(Action.INTERRUPT)
            return tuple(result)
        if state.zone == Zone.VILLAGE:
            return (Action.ROUTE_FOREST, Action.ROUTE_CAVE)
        options = ([Action.ADVANCE, Action.SCAVENGE, Action.ROUTE_TOWER]
                   if state.zone == Zone.SWAMP else [Action.ADVANCE, Action.SCAVENGE])
        if (state.xp >= self.TRAINING_COST and not state.trained
                and state.energy >= self.TRAINING_ENERGY_COST):
            options.append(Action.TRAIN)
        return tuple(options)

    @staticmethod
    def _combine(outcomes: list[Transition]) -> tuple[Transition, ...]:
        """Fusiona resultados idénticos para ahorrar cómputo en Value Iteration."""
        combined: dict[tuple[State, float], float] = {}
        for outcome in outcomes:
            if outcome.probability <= 0:
                continue
            key = (outcome.next_state, outcome.reward)
            combined[key] = combined.get(key, 0.0) + outcome.probability
        return tuple(Transition(probability=p, next_state=s, reward=r)
                     for (s, r), p in combined.items())

    def transitions(self, state: GameState, action: Action) -> tuple[Transition, ...]:
        if action not in self.actions(state):
            raise ValueError(f"Acción no válida: {action} en {state}")
        if state.enemy_hp > 0:
            outcomes = self._combat(state, action)
        else:
            outcomes = self._explore(state, action)
        total = sum(t.probability for t in outcomes)
        if abs(total - 1.0) > 1e-9:
            raise AssertionError(f"Transiciones sin normalizar: {state}, {action}, {total}")
        return outcomes

    def _explore(self, state: GameState, action: Action) -> tuple[Transition, ...]:
        if action == Action.TRAIN:
            # Elección irreversible entre gastar un turno y preparar ataques futuros.
            improved = replace(state, xp=state.xp - self.TRAINING_COST,
                               energy=state.energy - self.TRAINING_ENERGY_COST,
                               trained=True)
            return (Transition(1.0, improved, -3.0),)
        if state.zone == Zone.VILLAGE:
            destination = Zone.FOREST if action == Action.ROUTE_FOREST else Zone.CAVE
            energy = min(self.MAX_ENERGY, state.energy + (action == Action.ROUTE_CAVE))
            # La caverna da energía adicional pero expone a una emboscada inicial.
            ambush_p = 0.0 if destination == Zone.FOREST else 0.20
            resource_events = [(1.0, energy, state.potion, state.data_core)]
            advance_reward = 2.0
        else:
            if state.zone == Zone.FORTRESS:
                return (Transition(1.0, Ending.WIN, 100.0),)
            destination = {
                Zone.FOREST: Zone.SWAMP,
                Zone.CAVE: Zone.SWAMP,
                Zone.SWAMP: (Zone.TOWER if action == Action.ROUTE_TOWER else Zone.RUINS),
                Zone.RUINS: Zone.FORTRESS,
                Zone.TOWER: Zone.FORTRESS,
            }[state.zone]
            ambush_p = (0.37 if action == Action.ROUTE_TOWER
                        else 0.30 if action == Action.SCAVENGE else 0.10)
            energy = state.energy
            advance_reward = 3.0 if action == Action.ROUTE_TOWER else 2.0
            if action == Action.SCAVENGE:
                # Recompensa de exploración: suministros o núcleo de datos.
                resource_events = [(0.65, min(self.MAX_ENERGY, energy + 2), True, state.data_core),
                                   (0.35, energy, state.potion, state.data_core)]
                if state.zone in (Zone.SWAMP, Zone.RUINS, Zone.TOWER) and not state.data_core:
                    resource_events = [
                        (p * chance, en, pot, has_core)
                        for p, en, pot, _ in resource_events
                        for chance, has_core in ((0.35, True), (0.65, False))
                    ]
            elif action == Action.ROUTE_TOWER:
                # La torre es más arriesgada, pero permite recuperar energía
                # y tiene un 45 % de encontrar un núcleo de datos.
                resource_events = [(0.45, min(self.MAX_ENERGY, energy + 2), state.potion, True),
                                   (0.55, energy, state.potion, state.data_core)]
                if state.data_core:
                    resource_events = [(1.0, energy, state.potion, True)]
            else:
                resource_events = [(1.0, energy, state.potion, state.data_core)]

        outcomes: list[Transition] = []
        for p_resource, new_energy, new_potion, new_core in resource_events:
            for ambush, p_ambush in ((False, 1 - ambush_p), (True, ambush_p)):
                new_hp = state.hp - int(ambush)
                reward = advance_reward - (4.0 if ambush else 0.0) + (4.0 if new_core and not state.data_core else 0.0)
                next_state: State
                if new_hp <= 0:
                    next_state = Ending.LOSS
                    reward -= 80.0
                else:
                    next_state = GameState(
                        zone=destination,
                        hp=new_hp,
                        energy=new_energy,
                        enemy_hp=self.ENEMY_HP[destination],
                        evolved=state.evolved,
                        potion=new_potion,
                        enemy_charging=False,
                        data_core=new_core,
                        xp=state.xp,
                        trained=state.trained,
                    )
                outcomes.append(Transition(p_resource * p_ambush, next_state, reward))
        return self._combine(outcomes)

    def _combat(self, state: GameState, action: Action) -> tuple[Transition, ...]:
        hp = state.hp
        energy = state.energy
        evolved = state.evolved
        potion = state.potion
        damage = 0
        hit_probability = 1.0
        technique = technique_for(int(evolved)) if action == Action.TECHNIQUE else None

        if action == Action.ATTACK:
            damage = self.ATTACK_DAMAGE[int(evolved)] + int(state.trained)
            hit_probability = 0.90
        elif action == Action.POWER_ATTACK:
            energy -= 1
            damage = self.SPECIAL_DAMAGE[int(evolved)] + int(state.trained)
            hit_probability = 0.75
        elif action == Action.TECHNIQUE:
            assert technique is not None
            energy -= technique.energy_cost
            damage = technique.damage + int(state.trained)
            hit_probability = technique.hit_probability
        elif action == Action.GUARD:
            energy = min(self.MAX_ENERGY, energy + 2)
        elif action == Action.HEAL:
            hp = min(self.MAX_HP, hp + 3)
            potion = False
        elif action == Action.DIGIVOLVE:
            evolved = int(evolved) + 1
            energy -= self.EVOLUTION_COST[evolved]
        elif action == Action.INTERRUPT:
            energy -= 1

        outcomes: list[Transition] = []
        # Interrumpir solo está disponible ante un ataque anunciado. Si acierta,
        # cancela el golpe y hace 1 PS; si falla, el enemigo contraataca.
        if action == Action.INTERRUPT:
            damage, hit_probability = 1, 0.80
        own_attack_outcomes = (
            ((True, hit_probability), (False, 1.0 - hit_probability))
            if damage else ((False, 1.0),)
        )
        for hit, p_hit in own_attack_outcomes:
            # Piedmon posee armadura viral. Formas altas atraviesan su protección.
            armor = (max(0, 3 - int(state.evolved) - int(state.data_core))
                     if state.zone == Zone.FORTRESS else 0)
            # Las técnicas de etapas superiores perforan la armadura.
            effective_armor = max(0, armor - (technique.armor_piercing if technique else 0))
            # La interrupción ignora armadura: corta una habilidad, no un ataque normal.
            inflicted = min(state.enemy_hp, (1 if action == Action.INTERRUPT else
                         max(0, damage + (int(state.data_core) if state.zone == Zone.FORTRESS else 0) - effective_armor)) if hit else 0)
            enemy_hp = state.enemy_hp - inflicted
            base_reward = -1.0 + 3.0 * inflicted
            if enemy_hp == 0:
                if state.zone == Zone.FORTRESS:
                    outcomes.append(Transition(p_hit, Ending.WIN, base_reward + 100.0))
                else:
                    cleared = GameState(
                        state.zone, hp, energy, 0, evolved, potion, False, state.data_core,
                        min(self.MAX_XP, state.xp + 1), state.trained,
                    )
                    outcomes.append(Transition(p_hit, cleared, base_reward + 8.0))
                continue

            # El ataque interrumpido cancela el contraataque actual; el enemigo
            # puede volver a preparar otra habilidad en el próximo turno.
            interrupted = (action == Action.INTERRUPT and hit) or (
                action == Action.TECHNIQUE and hit and state.enemy_charging
                and technique is not None and technique.cancels_charged
            )
            enemy_hit_prob = (0.0 if interrupted else
                              min(0.98, self.ENEMY_HIT_PROB[state.zone] +
                                  (0.09 if state.enemy_charging else 0.0)))
            for foe_hit, p_foe in ((True, enemy_hit_prob), (False, 1.0 - enemy_hit_prob)):
                if p_foe == 0:
                    continue
                incoming = (self.ENEMY_DAMAGE[state.zone] +
                            (2 if state.enemy_charging else 0)) if foe_hit else 0
                # La resistencia distingue MetalGreymon (-1) de WarGreymon (-2).
                if incoming and evolved >= 2:
                    incoming = max(1, incoming - self.DAMAGE_REDUCTION[int(evolved)])
                if action == Action.GUARD and incoming:
                    # Defender reduce mucho un golpe cargado, nunca concede
                    # invulnerabilidad ilimitada (como exige un MDP episódico).
                    incoming = max(1, incoming - (3 if state.enemy_charging else 2))
                if action == Action.DIGIVOLVE and incoming:
                    incoming = max(0, incoming - (3 if evolved == 3 else 1))
                remaining = hp - incoming
                reward = base_reward - 4.0 * incoming
                if interrupted:
                    reward += 3.0  # premio por leer e interrumpir el ataque
                if remaining <= 0:
                    outcomes.append(Transition(p_hit * p_foe, Ending.LOSS, reward - 80.0))
                else:
                    charge_p = self.CHARGE_PROB[state.zone]
                    for charging, p_charge in ((False, 1 - charge_p), (True, charge_p)):
                        next_state = GameState(state.zone, remaining, energy, enemy_hp,
                                               evolved, potion, charging, state.data_core,
                                               state.xp, state.trained)
                        outcomes.append(Transition(p_hit * p_foe * p_charge,
                                                   next_state, reward))
        return self._combine(outcomes)

    def reachable_states(self) -> tuple[GameState, ...]:
        """BFS: computa solo estados que pueden aparecer desde el inicio."""
        start = self.start_state()
        visited: set[GameState] = {start}
        queue = deque([start])
        while queue:
            state = queue.popleft()
            for action in self.actions(state):
                for t in self.transitions(state, action):
                    if isinstance(t.next_state, GameState) and t.next_state not in visited:
                        visited.add(t.next_state)
                        queue.append(t.next_state)
        return tuple(sorted(visited, key=lambda s: (s.zone.value, s.hp, s.energy, s.enemy_hp, s.evolved, s.potion, s.enemy_charging, s.data_core, s.xp, s.trained)))

    @staticmethod
    def sample(outcomes: tuple[Transition, ...], rng: Random) -> Transition:
        u = rng.random()
        cumulative = 0.0
        for outcome in outcomes:
            cumulative += outcome.probability
            if u < cumulative:
                return outcome
        return outcomes[-1]  # protege frente a errores de coma flotante

    def episode(
        self,
        policy: Callable[[GameState, tuple[Action, ...], Random], Action],
        rng: Random,
        gamma: float = 0.95,
        max_steps: int = 80,
    ) -> Episode:
        current: State = self.start_state()
        trace: list[Step] = []
        total = 0.0
        discounted = 0.0
        for index in range(max_steps):
            if isinstance(current, Ending):
                break
            legal = self.actions(current)
            action = policy(current, legal, rng)
            if action not in legal:
                raise ValueError(f"La política propuso una acción ilegal: {action}")
            outcome = self.sample(self.transitions(current, action), rng)
            trace.append(Step(current, action, outcome.reward, outcome.next_state))
            total += outcome.reward
            discounted += gamma ** index * outcome.reward
            current = outcome.next_state
            if isinstance(current, Ending):
                break
        return Episode(tuple(trace), current, total, discounted,
                       truncated=not isinstance(current, Ending))
