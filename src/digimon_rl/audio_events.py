"""Eventos sonoros derivados de una secuencia visual ya resuelta. Sin RNG ni SDL."""
from __future__ import annotations
from dataclasses import dataclass
from .combat_feedback import IMPACT_FRACTION
from .domain import Action


@dataclass(frozen=True)
class SoundCue:
    time_ms: int
    name: str
    group: str = 'cast'
    gain: float = 1.


def combat_cues(animation) -> tuple[SoundCue,...]:
    cues = []; start = 0
    support = {Action.HEAL:'heal',Action.GUARD:'guard',Action.DIGIVOLVE:'evolve'}
    for beat in animation.beats:
        if beat.actor == 'status':
            cues.append(SoundCue(start,'cancel','impact'))
        else:
            name = beat.effect or support.get(animation.step.action)
            if name:
                cues.append(SoundCue(start+40,name,gain=.75 if beat.actor=='enemy' and not beat.charged else 1.))
            damage = [c for c in animation.feedback.changes_for(beat.actor) if c.kind in ('damage','miss')]
            if any(c.amount is not None and c.amount<0 for c in damage):
                cues.append(SoundCue(start+round(beat.duration_ms*IMPACT_FRACTION),'impact','impact',.7))
            elif any(c.amount==0 for c in damage):
                cues.append(SoundCue(start+round(beat.duration_ms*IMPACT_FRACTION),'no_hit','impact',.7))
        start += beat.duration_ms
    return tuple(sorted(cues,key=lambda c:c.time_ms))


class SoundTimeline:
    """Consume cada evento una vez; descarta sonidos atrasados en frames lentos."""
    def __init__(self,cues: tuple[SoundCue,...]):
        self.cues = tuple(sorted(cues,key=lambda c:c.time_ms))
        self.cursor = 0

    def advance(self,time_ms: int,*,max_lateness_ms: int=160) -> tuple[SoundCue,...]:
        due = []
        while self.cursor<len(self.cues) and self.cues[self.cursor].time_ms<=time_ms:
            cue = self.cues[self.cursor]; self.cursor += 1
            if time_ms-cue.time_ms <= max_lateness_ms:
                due.append(cue)
        return tuple(due)

    def discard(self) -> None:
        self.cursor = len(self.cues)
