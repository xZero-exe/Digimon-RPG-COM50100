"""Fichas oficiales estáticas y datos del RPG; no dependen de SDL ni de red."""
from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
from urllib.parse import urlparse
from .domain import Zone
from .environment import DigitalWorld
from .techniques import technique_for
from .session import ENEMY_SKILLS

@dataclass(frozen=True)
class DigiDexEntry:
    species: str
    name: str
    level: str
    kind: str
    attribute: str
    moves: tuple[str,...]
    profile: str
    source_url: str
    hero_form: int | None = None
    zone: Zone | None = None

    @property
    def role(self):return 'Protagonista' if self.hero_form is not None else 'Enemigo'

@lru_cache(maxsize=1)
def load_entries() -> tuple[DigiDexEntry,...]:
    data=json.loads((Path(__file__).parent/'data/digidex_v022.json').read_text(encoding='utf-8'))
    result=[]
    for row in data['entries']:
        url=urlparse(row['source_url'])
        if url.scheme!='https' or url.netloc!='digimon.net' or not url.path.startswith('/reference'):
            raise ValueError('La ficha requiere una fuente de la enciclopedia oficial')
        result.append(DigiDexEntry(row['species'],row['name'],row['level'],row['type'],row['attribute'],
            tuple(row['moves']),row['profile'],row['source_url'],row.get('hero_form'),
            Zone[row['zone']] if row.get('zone') else None))
    if len({e.species for e in result})!=len(result):raise ValueError('Especies repetidas')
    return tuple(result)


def rpg_facts(entry: DigiDexEntry) -> tuple[tuple[str,str],...]:
    w=DigitalWorld
    if entry.hero_form is not None:
        f=entry.hero_form;t=technique_for(f)
        return (('Ataque básico',f'{w.ATTACK_DAMAGE[f]} PS sin mejora'),
                ('Técnica del juego',t.name),('Técnica: coste',f'{t.energy_cost} EN'),
                ('Técnica: daño / acierto',f'{t.damage} PS / {t.hit_probability:.0%}'),
                ('Resistencia',f'Hasta {w.DAMAGE_REDUCTION[f]} PS por golpe'),
                ('Evolución siguiente',f'{w.FORM_NAMES[f+1]} · {w.EVOLUTION_COST[f+1]} EN' if f<3 else 'Forma máxima del juego'))
    z=entry.zone
    return (('Región',z.label),('Salud inicial',f'{w.ENEMY_HP[z]} PS'),
            ('Golpe normal',f'{w.ENEMY_DAMAGE[z]} PS base / {w.ENEMY_HIT_PROB[z]:.0%} de acierto'),
            ('Carga por turno',f'{w.CHARGE_PROB[z]:.0%}' + ('; 65% con 3 PS o menos' if z==Zone.ABYSS else '')),
            ('Armadura', '2; se abre al cargar' if z==Zone.ABYSS else '1; se abre al cargar' if z==Zone.TOWER else
             'Depende de tu forma y núcleo' if z==Zone.FORTRESS else 'Sin armadura adicional'),
            ('Ataque anunciado',ENEMY_SKILLS[z]))


def rpg_tip(entry: DigiDexEntry) -> str:
    if entry.hero_form is not None:
        t=technique_for(entry.hero_form)
        if entry.hero_form==0:return 'Reserva energía para digievolucionar. La mejora de ataque añade 1 PS de daño.'
        bits=[]
        if t.armor_piercing:bits.append(f'{t.name} perfora hasta {t.armor_piercing} puntos de armadura.')
        if t.cancels_charged:bits.append('Si acierta, puede cancelar el ataque anunciado.')
        return ' '.join(bits) or 'Administra la energía entre habilidades y evolución.'
    if entry.zone==Zone.ABYSS:return 'Victoria: núcleo y hasta 2 EN. Su armadura se abre al cargar; el golpe anunciado sigue siendo peligroso.'
    if entry.zone==Zone.TOWER:return 'Su armadura se abre al cargar. Puedes avanzar a la Fortaleza o desviarte al Abismo tras vencerlo.'
    if entry.zone==Zone.FORTRESS:return 'WarGreymon cuesta 2 EN y resiste más. El núcleo mejora el daño contra el jefe.'
    return 'Defender recupera hasta 2 EN. Interrumpir está disponible ante un ataque anunciado si tienes energía.'
