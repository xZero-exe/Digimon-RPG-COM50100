"""Secuencia visual de un turno ya resuelto, independiente de Pygame y del RNG.

Lee Step; nunca muestrea transiciones ni escribe en el entorno o las políticas.
"""
from __future__ import annotations
from dataclasses import dataclass, field, replace
from .domain import Action, Ending, GameState, Step, Zone
from .techniques import technique_for
from .combat_feedback import TurnFeedback, SETTLE_MS

HERO_EFFECTS = ('baby_flame', 'mega_flame', 'giga_destroyer', 'terra_force')
ENEMY_EFFECTS = {
    Zone.ABYSS: 'giga_destroyer',
    Zone.FOREST: 'electric_shock', Zone.CAVE: 'goblin_strike',
    Zone.SWAMP: 'haouken', Zone.RUINS: 'death_claw',
    Zone.TOWER: 'spiral_sword', Zone.FORTRESS: 'trump_sword',
}
EFFECT_LABELS = {
    'baby_flame': 'Baby Flame', 'mega_flame': 'Mega Flame',
    'giga_destroyer': 'Giga Destroyer', 'terra_force': 'Terra Force',
    'electric_shock': 'Electric Shock', 'goblin_strike': 'Goblin Strike',
    'haouken': 'Pummel Whack', 'death_claw': 'Death Claw',
    'spiral_sword': 'Spiral Sword', 'trump_sword': 'Trump Sword',
    'basic_attack': 'Ataque físico', 'power_attack': 'Ataque especial',
    'interrupt_strike': 'Interrumpir',
}
SIGNATURE_EFFECTS = HERO_EFFECTS + tuple(ENEMY_EFFECTS[z] for z in (Zone.FOREST,Zone.CAVE,Zone.SWAMP,Zone.RUINS,Zone.TOWER,Zone.FORTRESS))
BASIC_EFFECTS = {
    Action.ATTACK: 'basic_attack', Action.POWER_ATTACK: 'power_attack',
    Action.INTERRUPT: 'interrupt_strike',
}
ALL_EFFECTS = SIGNATURE_EFFECTS + tuple(BASIC_EFFECTS.values())


@dataclass(frozen=True)
class VisualBeat:
    actor: str
    effect: str | None
    title: str
    result: str
    duration_ms: int = 640
    charged: bool = False


@dataclass
class CombatAnimation:
    step: Step
    beats: tuple[VisualBeat, ...]
    elapsed_ms: int = 0
    feedback: TurnFeedback = field(init=False)

    def __post_init__(self) -> None:
        self.feedback = TurnFeedback.from_step(self.step)

    @classmethod
    def from_step(cls, step: Step) -> CombatAnimation | None:
        before, after = step.state, step.next_state
        if before.enemy_hp <= 0:
            return None
        defeated = after == Ending.WIN or isinstance(after, GameState) and after.enemy_hp == 0
        damaged = defeated or isinstance(after, GameState) and after.enemy_hp < before.enemy_hp
        offensive = step.action in (Action.ATTACK, Action.POWER_ATTACK, Action.TECHNIQUE, Action.INTERRUPT)
        effect = HERO_EFFECTS[int(before.evolved)] if step.action == Action.TECHNIQUE else BASIC_EFFECTS.get(step.action)
        title = EFFECT_LABELS[effect] if effect else {
            Action.ATTACK: 'Ataque', Action.POWER_ATTACK: 'Ataque especial',
            Action.INTERRUPT: 'Interrumpir', Action.GUARD: 'Defender',
            Action.HEAL: 'Poción', Action.DIGIVOLVE: 'Digievolución',
        }.get(step.action, 'Acción')
        # Un terminal de derrota no conserva los PS del enemigo; no inventar acierto/fallo.
        hero_result = ('GOLPE FINAL' if defeated else 'ATAQUE' if after == Ending.LOSS
                       else 'IMPACTO' if damaged else 'SIN DAÑO') if offensive else title.upper()
        if step.action == Action.INTERRUPT and isinstance(after,GameState) and not damaged:
            hero_result = 'FALLÓ'
        beats = [VisualBeat('hero', effect, title, hero_result)]
        interrupted = damaged and (step.action == Action.INTERRUPT or
            step.action == Action.TECHNIQUE and before.enemy_charging and
            technique_for(before.evolved).cancels_charged)
        if not defeated:
            if interrupted:
                beats.append(VisualBeat('status', None, 'Contraataque cancelado', 'INTERRUMPIDO', 280))
            else:
                # Una poción puede ocultar daño en la diferencia neta de PS.
                expected_hp = min(6, before.hp+3) if step.action == Action.HEAL else before.hp
                received = after == Ending.LOSS or isinstance(after, GameState) and after.hp < expected_hp
                foe_effect = ENEMY_EFFECTS[before.zone]
                beats.append(VisualBeat('enemy', foe_effect,
                    ('Destruction Grenade' if before.zone == Zone.ABYSS else EFFECT_LABELS[foe_effect]) if before.enemy_charging else 'Contraataque',
                    'IMPACTO' if received else 'SIN DAÑO', charged=before.enemy_charging))
        return cls(step, tuple(beats))

    @property
    def duration_ms(self) -> int:
        return sum(beat.duration_ms for beat in self.beats) + SETTLE_MS

    @property
    def active(self) -> bool:
        return self.elapsed_ms < self.duration_ms

    def update(self, delta_ms: int) -> None:
        self.elapsed_ms = min(self.duration_ms, self.elapsed_ms + max(0, delta_ms))

    def finish(self) -> None:
        self.elapsed_ms = self.duration_ms

    @property
    def current(self) -> tuple[VisualBeat, float] | None:
        time = self.elapsed_ms
        for beat in self.beats:
            if time < beat.duration_ms:
                return beat, time / beat.duration_ms
            time -= beat.duration_ms
        return None

    @property
    def display_state(self) -> GameState:
        before, after = self.step.state, self.step.next_state
        if (self.step.action == Action.DIGIVOLVE and
                self.elapsed_ms >= self.beats[0].duration_ms * .5):
            return replace(before, evolved=after.evolved if isinstance(after, GameState) else before.evolved+1)
        return before
