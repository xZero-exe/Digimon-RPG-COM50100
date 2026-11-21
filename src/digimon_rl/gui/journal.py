"""Vistas de Digidex y diario; consumen información estática y turnos observados."""
import pygame
from ..digidex import load_entries,rpg_facts,rpg_tip
from ..adventure_summary import summarize
from ..assets_catalog import HERO_SPRITES
from ..domain import Ending

CYAN=(87,226,229);GOLD=(255,192,96);WHITE=(232,243,250);MUTED=(165,184,198)
GREEN=(107,219,162);RED=(248,111,148);PANEL=(21,35,54)

class JournalViews:
    def _wrapped(self,text,x,y,width,*,font=None,color=WHITE,line_height=21):
        font=font or self.small;line='';lines=[]
        for word in str(text).split():
            candidate=(line+' '+word).strip()
            if line and font.size(candidate)[0]>width:lines.append(line);line=word
            else:line=candidate
        if line:lines.append(line)
        for i,value in enumerate(lines):
            self._text(value,x,y+i*line_height,font=self._fit_font(value,font,width),color=color)
        return y+len(lines)*line_height

    def _dex_entries(self):
        return tuple(e for e in load_entries() if self.dex_filter=='all' or
                     (e.hero_form is not None)==(self.dex_filter=='heroes'))

    def _draw_digidex(self):
        self._academic_shell('F7 · DIGIDEX DEL MUNDO DIGITAL',
            '11 fichas verificadas · 4 formas protagonistas y 7 enemigos · consulta sin consumir turnos')
        self._panel(pygame.Rect(62,124,298,621));self._panel(pygame.Rect(378,124,840,621))
        for i,(key,label) in enumerate([('all','Todos'),('heroes','Formas'),('enemies','Enemigos')]):
            self._button(pygame.Rect(70+i*94,137,88,33),label,'dex_filter',key,
                         size='small',selected=self.dex_filter==key)
        entries=self._dex_entries();entry=entries[self.dex_index%len(entries)]
        for i,row in enumerate(entries):
            y=188+i*46
            self._button(pygame.Rect(72,y,276,36),row.name,'dex_select',i,
                         selected=row==entry,size='small',accent=GOLD)
            icon=self.sprites.sprite(row.species,(29,29))
            if icon is not None:self.screen.blit(icon,icon.get_rect(center=(93,y+18)))
        self._text(entry.name,404,145,font=self.title,color=CYAN)
        self._text(entry.role + (' · '+entry.zone.label if entry.zone else ' · línea de Agumon'),405,184,font=self.small,color=MUTED)
        self._button(pygame.Rect(1025,146,166,34),'Fuente oficial ↗','dex_source',size='small')
        for i,(label,value) in enumerate([('NIVEL',entry.level),('TIPO',entry.kind),('ATRIBUTO',entry.attribute)]):
            self._text(label,405,224+i*30,font=self.small,color=MUTED)
            self._text(value,543,222+i*30,font=self.body,color=WHITE)
        self._text('TÉCNICAS · FICHA OFICIAL EN INGLÉS',405,326,font=self.small,color=GOLD)
        self._wrapped(' / '.join(entry.moves),405,351,564,font=self.body,line_height=23)
        pygame.draw.rect(self.screen,(12,25,42),(995,204,198,202),border_radius=14)
        pygame.draw.rect(self.screen,(63,108,130),(995,204,198,202),1,border_radius=14)
        image=self.sprites.sprite(entry.species,(175,181))
        if image is not None:self.screen.blit(image,image.get_rect(center=(1094,306)))
        self._wrapped(entry.profile,405,422,778,font=self.small,line_height=21)
        pygame.draw.line(self.screen,(61,88,111),(405,478),(1190,478),1)
        self._text('EN ESTE RPG',405,491,font=self.small,color=GOLD)
        self._text('Valores de juego; no son estadísticas oficiales de la franquicia.',584,493,font=self.tiny,color=MUTED)
        for i,(label,value) in enumerate(rpg_facts(entry)):
            y=521+i*24
            self._text(label,405,y,font=self.small,color=MUTED)
            self._text(value,637,y,font=self._fit_font(value,self.small,548),color=WHITE)
        self._wrapped(rpg_tip(entry),405,675,779,font=self.small,color=GREEN,line_height=21)
        note='Fuente: Digimon Encyclopedia · digimon.net · verificada el 06/11/2026'
        self._text(note,72,755,font=self.tiny,color=MUTED)
        self.tooltips.append((pygame.Rect(1025,146,166,34),entry.source_url))
        if self.dex_source_notice:
            self._text('Si no se abre el navegador, consulta el enlace de la ficha en la documentación.',405,718,font=self.tiny,color=GOLD)

    def _draw_adventure_summary(self):
        data=summarize(self.controller,self.inspector.gamma if self.inspector else .95)
        self._dark_veil(248)
        self._panel(pygame.Rect(40,35,1200,737))
        color=GREEN if self.controller.state==Ending.WIN else RED if self.controller.state==Ending.LOSS else GOLD if self.controller.finished else CYAN
        heading='MUNDO DIGITAL RESTAURADO' if self.controller.state==Ending.WIN else 'FIN DE LA AVENTURA' if self.controller.finished else 'DIARIO DE AVENTURA'
        self._text(heading,66,59,font=self.title,color=color)
        self._text(data.outcome,994,66,font=self._fit_font(data.outcome,self.small,216),color=color)
        subtitle='Tu recorrido y tus decisiones, guardados durante esta aventura.' if data.complete else 'Registro parcial: solo se muestran los turnos que se han registrado.'
        self._text(subtitle,67,104,font=self.small,color=MUTED)
        pygame.draw.line(self.screen,(57,87,110),(530,148),(530,718),1)
        form=data.forms[-1] if data.forms else 'Agumon'
        species=HERO_SPRITES[self.controller.world.FORM_NAMES.index(form)]
        image=self.sprites.sprite(species,(130,156))
        if image is not None:self.screen.blit(image,image.get_rect(center=(132,231)))
        self._text(form.upper(),222,164,font=self._fit_font(form.upper(),self.subtitle,292),color=GOLD)
        self._text('Control: '+data.mode,222,206,font=self.small)
        self._text(f'Semilla: {data.seed}',222,235,font=self.small,color=MUTED)
        self._text(f'{data.turns} turnos · {data.victories} combates ganados',222,264,font=self._fit_font(f'{data.turns} turnos · {data.victories} combates ganados',self.small,291))
        self._text('RECOMPENSA REGISTRADA',66,326,font=self.tiny,color=MUTED)
        self._text(f'{data.reward:+.1f}',66,349,font=self.title,color=CYAN)
        self._text(f'RETORNO · γ = {data.gamma:g}',285,326,font=self.tiny,color=MUTED)
        self._text(f'{data.discounted_return:+.2f}',285,349,font=self.title,color=CYAN)
        self._text('FORMAS UTILIZADAS',66,398,font=self.small,color=GOLD)
        self._wrapped(' → '.join(data.forms),66,423,440,font=self.small,line_height=20)
        self._text(data.resource_label.upper(),66,463,font=self.small,color=GOLD)
        last=data.last_observed
        self._text(f'PS {last.hp}/6  ·  EN {last.energy}/6  ·  Poción: '+('sí' if last.potion else 'no'),66,489,font=self.small)
        self._text('RECORRIDO',66,533,font=self.small,color=GOLD)
        self._wrapped(' → '.join(z.label for z in data.route),66,557,440,font=self.small,line_height=20)
        self._text('TÉCNICAS UTILIZADAS',66,643,font=self.small,color=GOLD)
        skills=' · '.join(f'{name} ×{count}' for name,count in data.techniques) or 'No se usaron técnicas especiales.'
        self._wrapped(skills,66,667,440,font=self.tiny,line_height=18)
        self._text(f'Pociones usadas: {data.potions_used}  ·  Acciones de respaldo: {data.fallback_actions}',66,710,font=self.tiny,color=MUTED)
        self._text('DECISIONES CLAVE',550,151,font=self.subtitle,color=CYAN)
        self._text('Acciones registradas · Abre T para consultar los valores del estado.',550,183,font=self.tiny,color=MUTED)
        pages=max(1,(len(data.moments)+3)//4);page=min(self.summary_page,pages-1)
        moments=data.moments[page*4:page*4+4]
        if not moments:self._wrapped('Todavía no hay decisiones clave registradas. El diario se completa a medida que juegas.',561,247,601,font=self.body)
        for i,moment in enumerate(moments):
            y=211+i*104
            pygame.draw.rect(self.screen,(27,44,65),(546,y-8,666,94),border_radius=10)
            self._text(f'Turno {moment.index+1} · {moment.title}',561,y+2,font=self.small,color=GOLD)
            self._text(moment.driver,1066,y+2,font=self._fit_font(moment.driver,self.tiny,133),color=RED if moment.fallback else MUTED)
            self._wrapped(moment.detail,561,y+29,475,font=self.tiny,line_height=18)
            self._button(pygame.Rect(1053,y+36,144,31),'T · Ver decisión','summary_inspect',moment.index,size='small')
        self._text(f'Página {page+1}/{pages} · {len(data.moments)} momentos',561,650,font=self.small,color=MUTED)
        self._button(pygame.Rect(968,638,104,35),'← Anterior','summary_shift',-1,size='small',enabled=page>0)
        self._button(pygame.Rect(1082,638,115,35),'Siguiente →','summary_shift',1,size='small',enabled=page<pages-1)
        self._wrapped('El diario describe acciones y efectos observados. El laboratorio compara DP y MC; no atribuye intenciones al agente.',551,698,645,font=self.tiny,color=MUTED,line_height=18)
        self._button(pygame.Rect(66,737,159,34),'↻ Nueva aventura','reset',size='small')
        self._button(pygame.Rect(236,737,104,34),'Menú','title',size='small')
        if not self.controller.finished:self._button(pygame.Rect(352,737,160,34),'Volver','back',size='small')
