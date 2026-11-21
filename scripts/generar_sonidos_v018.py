"""Sintetiza efectos retro originales y reproducibles con la biblioteca estándar.

No utiliza muestras, melodías ni archivos de audio de otros videojuegos.
No usa el generador aleatorio del entorno MDP.
"""
from __future__ import annotations
from array import array
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import wave

ROOT = Path(__file__).resolve().parents[1]
RATE = 22050


def voice(freq,duration,*,end=None,shape='triangle',amplitude=.4,seed=17):
    samples = []; phase = 0.; noise = seed
    count = round(duration*RATE)
    for i in range(count):
        t = i/RATE; f = freq if end is None else freq+(end-freq)*i/max(1,count-1)
        phase = (phase+f/RATE)%1
        if shape == 'noise':
            noise = (1664525*noise+1013904223)&0xffffffff
            value = (noise/0xffffffff)*2-1
        elif shape == 'square':
            value = 1. if phase<.3 else -.43
        elif shape == 'sine':
            value = math.sin(phase*math.tau)
        else:
            value = 1-4*abs(phase-.5)
        attack = min(1.,t/.004)
        release = min(1.,max(0.,(duration-t)/.014))
        envelope = attack*release*(1-i/max(1,count))**.65
        samples.append(value*amplitude*envelope)
    return samples


def render(layers):
    length = max(round(offset*RATE)+len(sound) for offset,sound in layers)
    mix = [0.]*length
    for offset,sound in layers:
        start = round(offset*RATE)
        for i,value in enumerate(sound):
            mix[start+i] += value
    peak = max(abs(x) for x in mix) or 1
    gain = min(1.,.72/peak)
    pcm = array('h',(round(x*gain*32767) for x in mix))
    if sys.byteorder!='little':
        pcm.byteswap()
    return pcm.tobytes()


def arpeggio(notes,step=.07,duration=.13,shape='triangle'):
    return [(i*step,voice(hz,duration,shape=shape)) for i,hz in enumerate(notes)]


def sound_designs():
    noise = lambda d,amp=.35: voice(1,d,shape='noise',amplitude=amp)
    return {
        'ui':arpeggio((720,960),.025,.045),
        'basic_attack':[(0,noise(.10)),(0,voice(210,.13,end=80,amplitude=.55))],
        'power_attack':[(0,voice(130,.22,end=500,shape='square')),(.10,noise(.17,.45))],
        'interrupt_strike':arpeggio((1300,1850,950),.035,.07,'square'),
        'baby_flame':[(0,noise(.23)),(0,voice(560,.20,end=160,shape='square',amplitude=.3))],
        'mega_flame':[(0,noise(.30,.45)),(0,voice(240,.32,end=70,amplitude=.5))],
        'giga_destroyer':arpeggio((340,510),.09,.13,'square')+[(.18,noise(.26,.5)),(.18,voice(120,.25,end=45))],
        'terra_force':arpeggio((330,440,660,880),.06,.16)+[(.22,voice(90,.35,end=50)),(.24,noise(.23))],
        'electric_shock':arpeggio((1600,1100,2000,1450),.038,.065,'square'),
        'goblin_strike':[(0,voice(170,.16,end=65,amplitude=.6)),(0,noise(.09,.35))],
        'haouken':[(0,voice(180,.29,end=850,shape='square')),(.08,voice(95,.24,end=45))],
        'death_claw':[(0,voice(1400,.12,end=250,shape='square')),(.10,noise(.14,.35))],
        'spiral_sword':arpeggio((750,1050,1500),.055,.12,'square'),
        'trump_sword':arpeggio((1175,880,1319,988),.05,.09,'square'),
        'heal':arpeggio((523,659,880),.075,.16),
        'guard':[(0,voice(240,.18,shape='sine')),(0,voice(760,.15,amplitude=.2))],
        'evolve':arpeggio((262,330,392,523,659,784),.075,.23)+[(.27,voice(1046,.37,shape='sine',amplitude=.24))],
        'impact':[(0,noise(.075,.35)),(0,voice(95,.10,end=45,amplitude=.4))],
        'no_hit':[(0,voice(1100,.10,end=700,amplitude=.18))],
        'cancel':arpeggio((1200,700,350),.045,.08,'square'),
        'travel':arpeggio((294,440,587,880),.07,.15)+[(.15,noise(.20,.08))],
        'victory':arpeggio((392,494,659,784),.12,.28),
        'loss':arpeggio((392,311,247,147),.13,.27),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'assets/audio')
    args = parser.parse_args(); args.output.mkdir(parents=True,exist_ok=True)
    files = []
    for name,layers in sound_designs().items():
        pcm = render(layers); path = args.output/(name+'.wav')
        with wave.open(str(path),'wb') as wav:
            wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(RATE); wav.writeframes(pcm)
        samples = array('h'); samples.frombytes(pcm)
        if sys.byteorder!='little': samples.byteswap()
        files.append({'file':path.name,'duration_ms':round(len(samples)*1000/RATE),
                      'peak':round(max(abs(n) for n in samples)/32767,4),
                      'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    (args.output/'manifest_v018.json').write_text(json.dumps({'version':'0.18','sample_rate':RATE,
        'channels':1,'sample_bits':16,'source':'Original deterministic synthesis; no third-party samples',
        'generator':'scripts/generar_sonidos_v018.py','files':files},ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'{len(files)} efectos WAV generados en {args.output}')


if __name__=='__main__':
    main()
