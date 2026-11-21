"""Habilidades por digievolución; efectos inmediatos, sin estado oculto.

Son datos inmutables del MDP. Ningún algoritmo de aprendizaje se implementa
ni modifica aquí: los dos agentes interactúan con el mismo `DigitalWorld`.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Technique:
    name: str
    energy_cost: int
    damage: int
    hit_probability: float
    armor_piercing: int = 0
    cancels_charged: bool = False


TECHNIQUES: tuple[Technique, ...] = (
    Technique('Baby Flame', 1, 2, 0.90),
    Technique('Mega Flame', 2, 4, 0.80, cancels_charged=True),
    Technique('Giga Destroyer', 2, 5, 0.80, armor_piercing=2),
    Technique('Terra Force', 3, 8, 0.85, armor_piercing=3, cancels_charged=True),
)


def technique_for(form: int) -> Technique:
    """Datos constantes para Agumon (0) ... WarGreymon (3)."""
    return TECHNIQUES[form]
