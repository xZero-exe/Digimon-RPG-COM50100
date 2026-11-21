"""Transición de presentación entre regiones; no agrega pasos al MDP."""
from dataclasses import dataclass
from .domain import GameState, Step


@dataclass
class RegionTransition:
    step: Step
    elapsed_ms: int = 0
    duration_ms: int = 560

    @classmethod
    def from_step(cls,step: Step):
        after = step.next_state
        if isinstance(after,GameState) and after.zone != step.state.zone:
            return cls(step)
        return None

    @property
    def active(self) -> bool:
        return self.elapsed_ms < self.duration_ms

    @property
    def progress(self) -> float:
        return min(1.,max(0.,self.elapsed_ms/self.duration_ms))

    @property
    def opacity(self) -> int:
        return round(235*(1-abs(2*self.progress-1)))

    @property
    def display_state(self) -> GameState:
        return self.step.state if self.progress<.5 else self.step.next_state

    def update(self,delta_ms: int) -> None:
        self.elapsed_ms = min(self.duration_ms,self.elapsed_ms+max(0,delta_ms))

    def finish(self) -> None:
        self.elapsed_ms = self.duration_ms
