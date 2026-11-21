"""Preferencias de audio por usuario; errores de lectura/escritura no bloquean el juego."""
from dataclasses import dataclass, asdict
import json
import math
import os
from pathlib import Path


def default_audio_path() -> Path:
    base = os.environ.get('APPDATA') if os.name=='nt' else os.environ.get('XDG_CONFIG_HOME')
    root = Path(base) if base else Path.home()/('.config' if os.name!='nt' else 'AppData/Roaming')
    return root/'Digimon_RPG_RL'/'audio.json'


@dataclass(frozen=True)
class AudioSettings:
    volume: float = .35
    muted: bool = False

    @classmethod
    def load(cls,path: Path):
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
            if not isinstance(data,dict):
                return cls()
            volume = data.get('volume',.35)
            if isinstance(volume,bool) or not isinstance(volume,(int,float)) or not math.isfinite(volume):
                volume = .35
            muted = data.get('muted',False)
            return cls(min(1.,max(0.,float(volume))),muted if isinstance(muted,bool) else False)
        except (OSError,ValueError,TypeError):
            return cls()

    def save(self,path: Path) -> bool:
        try:
            path.parent.mkdir(parents=True,exist_ok=True)
            temp = path.with_suffix('.tmp')
            temp.write_text(json.dumps(asdict(self),indent=2)+'\n',encoding='utf-8')
            temp.replace(path)
            return True
        except OSError:
            return False
