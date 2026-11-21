"""Resumen de una única aventura, derivado de los turnos realmente ejecutados.

No simula decisiones, calcula políticas ni infiere motivos del agente.
"""
from dataclasses import dataclass
from collections import Counter
from .domain import Action,Ending,GameState,Step,Zone
from .environment import DigitalWorld
from .session import AdventureController,ControlMode
from .techniques import technique_for

MODE_LABELS={ControlMode.DYNAMIC_PROGRAMMING:'Value Iteration',ControlMode.MONTE_CARLO:'Monte Carlo',ControlMode.MANUAL:'Manual'}

@dataclass(frozen=True)
class DecisionMoment:
    index: int
    title: str
    detail: str
    driver: str
    fallback: bool

@dataclass(frozen=True)
class AdventureSummary:
    outcome: str
    mode: str
    seed: int
    turns: int
    reward: float
    discounted_return: float
    gamma: float
    route: tuple[Zone,...]
    forms: tuple[str,...]
    victories: int
    potions_used: int
    techniques: tuple[tuple[str,int],...]
    fallback_actions: int
    last_observed: GameState
    resource_label: str
    moments: tuple[DecisionMoment,...]
    complete: bool


def summarize(controller: AdventureController,gamma: float=.95) -> AdventureSummary:
    if not 0<gamma<1:raise ValueError('gamma debe estar entre 0 y 1')
    records=tuple(controller.decisions);steps=tuple(r.step for r in records)
    route=[];forms=[];skills=Counter();moments=[];wins=0
    def remember(state):
        if not route or route[-1]!=state.zone:route.append(state.zone)
        if state.form_name not in forms:forms.append(state.form_name)
    for i,(record,step) in enumerate(zip(records,steps)):
        before,after=step.state,step.next_state;remember(before)
        if isinstance(after,GameState):remember(after)
        if step.action==Action.DIGIVOLVE:
            target=DigitalWorld.FORM_NAMES[before.evolved+1]
            if target not in forms:forms.append(target)
        if step.action==Action.TECHNIQUE:skills[technique_for(before.evolved).name]+=1
        if before.enemy_hp>0 and (after==Ending.WIN or isinstance(after,GameState) and after.enemy_hp==0):wins+=1
        title=detail=None
        if step.action in (Action.ROUTE_FOREST,Action.ROUTE_CAVE,Action.ROUTE_TOWER,Action.ROUTE_ABYSS,Action.ROUTE_REFUGE):
            title='Desvío al Refugio' if step.action==Action.ROUTE_REFUGE else 'Ruta al Abismo' if step.action==Action.ROUTE_ABYSS else 'Elección de ruta'
            detail=after.zone.label if isinstance(after,GameState) else before.zone.label
            if step.action==Action.ROUTE_REFUGE and isinstance(after,GameState):
                detail+=f': PS {before.hp} → {after.hp}; EN {before.energy} → {after.energy}; poción disponible.'
        elif step.action==Action.DIGIVOLVE:
            title='Digievolución';detail=f'{before.form_name} → {DigitalWorld.FORM_NAMES[before.evolved+1]}'
        elif step.action==Action.HEAL:
            title='Uso de poción';detail='Poción consumida.'
            if isinstance(after,GameState):detail+=f' PS antes/después del turno: {before.hp} → {after.hp}.'
        elif step.action==Action.INTERRUPT:
            title='Interrupción';detail='Acción ante un golpe enemigo anunciado; consulta el resultado del turno.'
        elif step.action==Action.GUARD and before.enemy_charging:
            title='Defensa ante carga';detail='El enemigo había anunciado un ataque potente.'
        elif step.action==Action.TRAIN:
            title='Entrenamiento';detail='Mejora permanente activada; se gastan XP y energía.'
        if title:
            driver='Respaldo' if record.fallback else MODE_LABELS[record.driver]
            moments.append(DecisionMoment(i,title,detail,driver,record.fallback))
    current=controller.state
    last=current if isinstance(current,GameState) else steps[-1].state if steps else controller.world.start_state()
    complete=(len(steps)==controller.turn and
              (steps[0].state==controller.world.start_state() and steps[-1].next_state==current
               if steps else current==controller.world.start_state()))
    # Los terminales no conservan todos los recursos: se muestra el estado anterior.
    label='Recursos actuales' if isinstance(current,GameState) else 'Antes del turno final'
    if not steps:remember(last)
    return AdventureSummary(controller.outcome,MODE_LABELS[controller.mode],controller.episode_seed,
        controller.turn,sum(s.reward for s in steps),sum(gamma**i*s.reward for i,s in enumerate(steps)),gamma,
        tuple(route),tuple(forms),wins,sum(s.action==Action.HEAL for s in steps),tuple(skills.items()),
        sum(r.fallback for r in records),last,label,tuple(moments),complete)
