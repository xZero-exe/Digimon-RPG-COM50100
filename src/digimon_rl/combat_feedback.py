"""Datos de presentación de un turno resuelto; no muestrea ni resuelve combates.

Las cifras son PS efectivos (limitados por la vida disponible), no daño bruto.
Un terminal LOSS no retiene los PS enemigos: ese dato se mantiene desconocido.
"""
from __future__ import annotations

from dataclasses import dataclass
from .domain import Action, Ending, GameState, Step
from .environment import DigitalWorld
from .techniques import technique_for

IMPACT_FRACTION = .60
TWEEN_MS = 190
POPUP_MS = 680
SETTLE_MS = 420


@dataclass(frozen=True)
class VitalChange:
    target: str  # hero, enemy, energy
    amount: int | None
    kind: str  # damage, heal, energy, unknown

    @property
    def text(self) -> str:
        if self.amount is None:
            return 'ATAQUE'
        if self.amount == 0:
            return 'FALLÓ' if self.kind == 'miss' else 'SIN DAÑO'
        unit = 'EN' if self.target == 'energy' else 'PS'
        return f'{self.amount:+d} {unit}'


@dataclass(frozen=True)
class VitalFrame:
    hero_hp: float
    enemy_hp: float | None
    energy: float


@dataclass(frozen=True)
class FloatingNotice:
    target: str
    text: str
    kind: str
    progress: float


@dataclass(frozen=True)
class TurnFeedback:
    initial: VitalFrame
    hero_changes: tuple[VitalChange, ...]
    enemy_changes: tuple[VitalChange, ...]

    @classmethod
    def from_step(cls, step: Step) -> TurnFeedback:
        before, after = step.state, step.next_state
        healed_hp = (min(DigitalWorld.MAX_HP, before.hp + 3)
                     if step.action == Action.HEAL else before.hp)
        # En estados normales se leen directamente los recursos resultantes.
        if isinstance(after, GameState):
            final_hp, final_enemy, final_energy = after.hp, after.enemy_hp, after.energy
        else:
            final_hp = 0 if after == Ending.LOSS else healed_hp
            final_enemy = 0 if after == Ending.WIN else None
            # Los terminales no guardan energía. Solo se presenta el costo/recurso
            # determinista de la acción, con las constantes compartidas del motor.
            cost = {Action.POWER_ATTACK: 1, Action.INTERRUPT: 1}.get(step.action, 0)
            if step.action == Action.TECHNIQUE:
                cost = technique_for(before.evolved).energy_cost
            elif step.action == Action.DIGIVOLVE:
                cost = DigitalWorld.EVOLUTION_COST[before.evolved + 1]
            final_energy = (min(DigitalWorld.MAX_ENERGY, before.energy+2)
                            if step.action == Action.GUARD else before.energy-cost)
        own: list[VitalChange] = []
        if healed_hp != before.hp:
            own.append(VitalChange('hero', healed_hp-before.hp, 'heal'))
        if final_energy != before.energy:
            own.append(VitalChange('energy', final_energy-before.energy, 'energy'))
        if step.action in (Action.ATTACK, Action.POWER_ATTACK, Action.TECHNIQUE, Action.INTERRUPT):
            kind = 'unknown' if final_enemy is None else 'damage'
            # Interrumpir ignora armadura: cero daño sí permite identificar
            # inequívocamente un fallo, a diferencia de otros ataques.
            if step.action == Action.INTERRUPT and final_enemy == before.enemy_hp:
                kind = 'miss'
            own.append(VitalChange('enemy', None if final_enemy is None else final_enemy-before.enemy_hp,
                                   kind))
        counter = (VitalChange('hero', final_hp-healed_hp, 'damage'),)
        if after == Ending.LOSS:
            counter += (VitalChange('enemy', None, 'unknown'),)
        return cls(VitalFrame(before.hp, before.enemy_hp, before.energy), tuple(own), counter)

    def changes_for(self, actor: str) -> tuple[VitalChange, ...]:
        return self.hero_changes if actor == 'hero' else self.enemy_changes if actor == 'enemy' else ()

    def sample(self, beats, elapsed_ms: int) -> VitalFrame:
        values: dict[str, float | None] = {'hero': self.initial.hero_hp,
                                         'enemy': self.initial.enemy_hp,
                                         'energy': self.initial.energy}
        start = 0
        for beat in beats:
            impact = start + beat.duration_ms * IMPACT_FRACTION
            fraction = min(1., max(0., (elapsed_ms-impact)/TWEEN_MS))
            # Ease-out: termina exactamente en el recurso real, sin acumular error.
            fraction = 1-(1-fraction)**2
            for change in self.changes_for(beat.actor):
                if change.amount is None:
                    if elapsed_ms >= impact:
                        values[change.target] = None
                elif values[change.target] is not None:
                    values[change.target] += change.amount*fraction
            start += beat.duration_ms
        return VitalFrame(values['hero'], values['enemy'], values['energy'])

    def notices(self, beats, elapsed_ms: int) -> tuple[FloatingNotice, ...]:
        notices = []
        start = 0
        for beat in beats:
            age = elapsed_ms - (start + beat.duration_ms * IMPACT_FRACTION)
            if 0 <= age < POPUP_MS:
                for change in self.changes_for(beat.actor):
                    # No se afirma acierto, fallo ni daño enemigo si el terminal
                    # descartó el dato; el nombre del ataque sigue visible.
                    if change.kind != 'unknown':
                        notices.append(FloatingNotice(change.target, change.text,
                                                      change.kind, age/POPUP_MS))
                if beat.actor == 'status':
                    notices.append(FloatingNotice('enemy', 'CANCELADO', 'cancel', age/POPUP_MS))
            start += beat.duration_ms
        return tuple(notices)

    def flash_for(self, beats, elapsed_ms: int, actor: str) -> str | None:
        start = 0
        for beat in beats:
            age = elapsed_ms - (start + beat.duration_ms * IMPACT_FRACTION)
            if 0 <= age < 140:
                for change in self.changes_for(beat.actor):
                    if change.target == actor and change.amount and change.kind in ('damage','heal'):
                        return change.kind
            start += beat.duration_ms
        return None
