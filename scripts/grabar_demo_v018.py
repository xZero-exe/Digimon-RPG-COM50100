"""Exporta un montaje diagnóstico con el render real y los WAV del juego.

Solo lo importa el diagnóstico cuando se pide --video. FFmpeg no es requisito
del juego. El audio se compone a partir de los mismos eventos del reproductor.
"""
from array import array
import json
from pathlib import Path
from random import Random
import shutil
import subprocess
import sys
import tempfile
import wave


def record_demo(app,world,output: Path):
    import pygame
    from digimon_rl.audio_settings import AudioSettings
    from digimon_rl.domain import Action, Ending, GameState, Zone
    from digimon_rl.presentation import Screen
    from digimon_rl.session import ControlMode
    executable=shutil.which('ffmpeg')
    if executable is None:
        raise RuntimeError('La exportación opcional de video requiere FFmpeg; el juego no lo necesita.')
    output.mkdir(parents=True,exist_ok=True)
    fps=25; frame_count=0; events=[]
    original_observer=app.audio.observer
    original_settings=app.audio.settings
    app.audio.settings=AudioSettings(.55,False);app.audio._apply_volume()
    app.audio.observer=lambda name,group,gain:events.append({
        'time':frame_count/fps,'name':name,'group':group,'gain':app.audio.effective_volume*gain})
    destination=output/'Vista_Previa_Sonido_v018.mp4'
    try:
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);silent=root/'video.mp4';wavfile=root/'audio.wav'
            command=[executable,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24',
                     '-s','1024x656','-r',str(fps),'-i','pipe:0','-an','-c:v','libx264',
                     '-preset','veryfast','-crf','21','-pix_fmt','yuv420p',str(silent)]
            process=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=subprocess.PIPE)

            def frames(seconds,label):
                nonlocal frame_count
                for _ in range(round(seconds*fps)):
                    app.draw()
                    app._text('DEMOSTRACIÓN · '+label,52,84,font=app.tiny,color=(87,226,229))
                    image=pygame.transform.smoothscale(app.screen,(1024,656))
                    process.stdin.write(pygame.image.tostring(image,'RGB'))
                    frame_count+=1;app.frames+=1;app._update_combat_visuals(40)

            def setup(state,action,predicate):
                app.audio.stop_gameplay()
                app.controller.state=state;app.controller.mode=ControlMode.MANUAL
                app.controller.turn=0;app.controller.reward=0;app.controller.last_report=None
                app.controller.history=['Demostración visual y sonora.']
                app.controller.visited_zones={Zone.VILLAGE,state.zone}
                app.inspection_history=[world.start_state(),state]
                app.presentation.screen=Screen.GAME
                app.region_transition=None;app.combat_animation=None
                app.animation_speed=1;app.notice_ticks=0;app.cue_ticks=0;app.fx_ticks=0
                outcomes=world.transitions(state,action)
                for seed in range(1000):
                    outcome=world.sample(outcomes,Random(seed))
                    if predicate(outcome.next_state):
                        app.controller.rng=Random(seed);break
                else:
                    raise AssertionError('No se encontró el resultado diagnóstico')
                app._advance(action);app.notice_ticks=0

            try:
                app._new_adventure(ControlMode.MANUAL);app.notice_ticks=0
                app.audio.play('ui','ui');frames(.24,'BOTONES')
                app._advance(Action.ROUTE_FOREST);app.notice_ticks=0
                frames(1.,'CAMBIO DE REGIÓN')
                setup(GameState(Zone.FOREST,6,3,2,0,True),Action.ATTACK,
                      lambda s:isinstance(s,GameState) and s.enemy_hp==1 and s.hp==5)
                frames(1.88,'ATAQUE Y CONTRAATAQUE')
                setup(GameState(Zone.FOREST,2,3,2,0,True,True),Action.HEAL,
                      lambda s:isinstance(s,GameState) and s.hp==2)
                frames(1.88,'CURACIÓN Y DAÑO POR SEPARADO')
                setup(GameState(Zone.RUINS,4,6,4,1,True,True),Action.DIGIVOLVE,
                      lambda s:isinstance(s,GameState) and s.evolved==2 and s.hp==2)
                frames(1.88,'DIGIEVOLUCIÓN')
                setup(GameState(Zone.SWAMP,5,3,3,0,True,True),Action.INTERRUPT,
                      lambda s:isinstance(s,GameState) and s.enemy_hp==2)
                frames(1.52,'INTERRUPCIÓN')
                setup(GameState(Zone.FORTRESS,6,6,2,3,True),Action.TECHNIQUE,lambda s:s==Ending.WIN)
                frames(1.92,'TERRA FORCE Y VICTORIA')
                process.stdin.close()
                errors=process.stderr.read().decode(errors='replace')
                if process.wait(timeout=30)!=0:
                    raise RuntimeError(errors)
            finally:
                if process.poll() is None:
                    process.kill();process.wait()
            rate=22050;mix=[0.]*round(frame_count/fps*rate)
            for i,event in enumerate(events):
                with wave.open(str(app.audio.root/(event['name']+'.wav')),'rb') as wav:
                    assert wav.getframerate()==rate and wav.getnchannels()==1
                    pcm=array('h');pcm.frombytes(wav.readframes(wav.getnframes()))
                    if sys.byteorder!='little':pcm.byteswap()
                start=round(event['time']*rate)
                limit=min(len(pcm),len(mix)-start)
                next_event=next((e for e in events[i+1:] if e['group']==event['group']),None)
                if next_event:
                    limit=min(limit,round(next_event['time']*rate)-start)
                for n in range(max(0,limit)):
                    mix[start+n]+=pcm[n]/32767*event['gain']
            peak=max(abs(v) for v in mix) or 1
            gain=min(1.,.94/peak)
            pcm=array('h',(round(v*gain*32767) for v in mix))
            if sys.byteorder!='little':pcm.byteswap()
            with wave.open(str(wavfile),'wb') as wav:
                wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(rate);wav.writeframes(pcm.tobytes())
            subprocess.run([executable,'-y','-loglevel','error','-i',str(silent),'-i',str(wavfile),
                            '-c:v','copy','-c:a','aac','-b:a','128k','-movflags','+faststart',
                            '-shortest',str(destination)],check=True,timeout=60)
            (output/'eventos_video_v018.json').write_text(json.dumps({
                'purpose':'Montage of legal diagnostic scenarios; not a learning experiment',
                'audio_source':'Same WAV assets and events as the game; composed offline for export',
                'seconds':frame_count/fps,'frames':frame_count,'sample_peak':round(peak*gain,4),
                'events':events},ensure_ascii=False,indent=2),encoding='utf-8')
    finally:
        app.audio.observer=original_observer;app.audio.settings=original_settings;app.audio._apply_volume()
    return destination
