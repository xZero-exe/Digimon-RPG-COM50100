"""Genera arte pixelado ORIGINAL para el prototipo educativo Digimon RPG.

No descarga ni extrae sprites de Digidex u otros juegos. Las ilustraciones
son interpretaciones fan-made creadas con primitivas de Pillow.

Uso: python -m pip install Pillow
     python scripts/generate_demo_art.py
"""
from __future__ import annotations

from pathlib import Path
import math
import random

from PIL import Image, ImageDraw, PngImagePlugin

ROOT = Path(__file__).resolve().parents[1]
DIGI = ROOT / 'assets' / 'demo' / 'digimon'
BACK = ROOT / 'assets' / 'demo' / 'backgrounds'
INK = (30, 30, 49, 255)
CREAM = (255, 243, 205, 255)
WHITE = (254, 252, 245, 255)

def rgb(s: str):
    s=s.lstrip('#'); return tuple(bytes.fromhex(s))+(255,)

class Painter:
    def __init__(self, size=128):
        self.img=Image.new('RGBA',(size,size),(0,0,0,0)); self.d=ImageDraw.Draw(self.img)
    def poly(self,xy, fill, outline=INK, width=3):
        self.d.polygon(xy,fill=fill)
        if outline: self.d.line(list(xy)+[xy[0]],fill=outline,width=width,joint='curve')
    def ell(self,box,fill,outline=INK,width=3): self.d.ellipse(box,fill=fill,outline=outline,width=width if outline else 1)
    def rect(self,box,fill,outline=INK,width=3): self.d.rectangle(box,fill=fill,outline=outline,width=width if outline else 1)
    def line(self,coords,fill=INK,width=3): self.d.line(coords,fill=fill,width=width,joint='curve')
    def eye(self,x,y,scale=1,angry=False):
        r=6*scale
        self.ell((x-r,y-r,x+r,y+r),WHITE,width=max(2,2*scale))
        self.ell((x-2*scale,y-2*scale,x+2*scale,y+3*scale),rgb('#26334c'),outline=None)
        self.ell((x-1*scale,y-2*scale,x,y-1*scale),WHITE,outline=None)
        if angry:self.line([(x-r,y-r-1),(x+r,y-r+1)],width=max(2,2*scale))
    def spark(self,x,y,color=CREAM):
        self.line([(x-4,y),(x+4,y)],color,2);self.line([(x,y-4),(x,y+4)],color,2)
    def save(self,name):
        info=PngImagePlugin.PngInfo();info.add_text('Artwork','Original procedural fan artwork for a noncommercial class prototype; NOT from Digidex.')
        self.img.save(DIGI/f'{name}.png',pnginfo=info)

def hero_agumon():
    p=Painter(); orange=rgb('#f6a72f'); amber=rgb('#d87621'); shine=rgb('#ffd565')
    p.ell((24,113,108,124),(11,21,37,83),outline=None)
    p.poly([(37,77),(18,68),(5,52),(20,88),(42,101),(66,97)], amber)
    p.poly([(29,74),(9,60),(11,75),(26,91)],shine,width=2)
    p.poly([(47,60),(74,61),(91,87),(80,113),(49,111),(33,90)],orange)
    p.ell((54,81,79,106),shine,outline=None)
    p.poly([(54,98),(42,120),(61,120),(68,106)],orange)
    p.poly([(77,99),(72,120),(95,119),(94,105)],orange)
    for x,y in [(44,119),(52,119),(76,118),(85,118)]:p.poly([(x,y-3),(x+6,y),(x,y+4)],CREAM,width=1)
    p.poly([(76,75),(108,74),(104,88),(88,95),(70,87)],orange)
    p.poly([(41,26),(54,18),(79,24),(98,32),(110,49),(124,49),(126,64),(105,76),(70,72),(48,60)],orange)
    p.poly([(52,28),(69,24),(89,29),(80,37),(54,41)],shine,outline=None)
    p.poly([(94,56),(116,55),(112,66),(95,69)],amber,outline=None)
    p.eye(91,45)
    p.ell((114,55,118,59),INK,outline=None)
    p.line([(93,65),(108,68),(120,64)],rgb('#93451a'),2)
    for x in (109,118):p.poly([(x,66),(x+3,66),(x+1,72)],CREAM,width=1)
    p.poly([(70,74),(81,76),(86,88),(78,95),(73,85)],orange)
    for x,y in [(79,92),(84,90)]:p.poly([(x,y),(x+8,y+2),(x+5,y+7)],CREAM,width=1)
    p.spark(35,26,shine)
    p.save('agumon')

def hero_greymon():
    p=Painter();orange=rgb('#e77b29');dark=rgb('#ac431e');armor=rgb('#e6e7d2');light=rgb('#fab14a')
    p.ell((16,112,112,125),(14,19,40,89),outline=None)
    p.poly([(42,79),(10,62),(4,39),(7,85),(39,102),(72,95)],dark)
    for x,y in [(13,46),(24,67),(39,77)]:p.poly([(x-7,y+3),(x,y-11),(x+5,y+7)],armor,width=2)
    p.poly([(39,68),(79,65),(100,96),(85,113),(45,108),(28,89)],orange)
    p.poly([(55,74),(79,80),(84,105),(51,105)],light,width=2)
    p.poly([(46,98),(36,121),(61,120),(71,105)],orange)
    p.poly([(80,101),(80,122),(109,120),(101,98)],orange)
    for x in (47,55,88,98):p.poly([(x,116),(x+6,117),(x+2,123)],armor,width=1)
    p.poly([(34,30),(43,15),(61,16),(67,9),(82,18),(93,24),(96,52),(121,51),(126,65),(104,73),(82,65),(48,69)],orange)
    p.poly([(34,31),(33,11),(46,20),(59,9),(55,36)],armor)
    p.poly([(62,22),(67,5),(80,16),(78,34)],armor)
    p.poly([(81,27),(95,11),(105,29),(106,44),(88,42)],armor)
    p.poly([(38,36),(64,25),(86,33),(90,59),(69,67),(45,58)],armor,width=2)
    p.poly([(52,37),(75,33),(82,40),(66,49)],rgb('#bcb5a7'),outline=None)
    p.eye(89,43,angry=True)
    p.ell((111,56,115,60),INK,outline=None)
    p.poly([(92,63),(121,63),(113,72),(95,69)],rgb('#6c3233'),width=2)
    for x in (100,109,117):p.poly([(x,63),(x+3,64),(x+1,69)],CREAM,width=1)
    p.poly([(76,78),(92,75),(98,87),(82,97)],orange)
    for x in [86,93]:p.poly([(x,94),(x+7,94),(x+2,101)],armor,width=1)
    p.save('greymon')

def betamon():
    p=Painter();green=rgb('#4fc86f');lime=rgb('#9eea75');deep=rgb('#278a72');fin=rgb('#ed8451')
    p.ell((12,112,109,123),(11,21,37,78),outline=None)
    p.poly([(18,78),(9,64),(15,54),(30,74)],deep)
    for x,y in [(32,67),(45,52),(60,44),(73,52),(83,65)]:p.poly([(x-10,y+14),(x-2,y-8),(x+10,y+14)],fin,width=2)
    p.ell((20,64,111,113),green)
    p.ell((35,83,97,108),lime,outline=None)
    p.poly([(24,94),(12,107),(34,112),(43,101)],deep)
    p.poly([(84,93),(82,114),(108,113),(109,104)],deep)
    p.poly([(62,52),(77,41),(94,48),(103,66),(119,68),(123,85),(105,95),(79,88),(63,77)],green)
    p.poly([(94,74),(113,72),(116,85),(95,87)],lime,outline=None)
    p.eye(89,57)
    p.ell((111,76,116,80),INK,outline=None)
    p.line([(86,87),(106,91),(119,85)],deep,2)
    for x,y in [(43,77),(54,71),(65,82),(47,92)]:p.ell((x,y,x+6,y+4),deep,outline=None)
    p.save('betamon')

def goblimon():
    p=Painter();green=rgb('#73b674');shade=rgb('#347f5c');hair=rgb('#eaa35b');wood=rgb('#866044')
    p.ell((21,116,117,125),(11,21,37,78),outline=None)
    p.poly([(38,72),(77,70),(87,102),(75,115),(39,112),(29,91)],green)
    p.poly([(44,102),(35,121),(54,121),(61,107)],shade)
    p.poly([(67,104),(68,123),(88,123),(81,102)],shade)
    p.rect((101,33,109,108),wood,width=2)
    p.poly([(92,22),(117,16),(127,30),(124,54),(99,59),(85,38)],rgb('#b3aca2'))
    p.poly([(46,22),(62,11),(75,19),(87,33),(91,59),(76,80),(41,70),(29,52)],green)
    p.poly([(36,33),(12,27),(25,53),(39,56)],green)
    p.poly([(85,35),(102,25),(92,53),(83,54)],green)
    p.poly([(42,21),(47,5),(58,20),(64,8),(74,25)],hair)
    p.eye(70,43,angry=True)
    p.poly([(65,55),(89,53),(82,66),(67,65)],rgb('#a5d883'),width=2)
    p.poly([(84,60),(91,58),(85,73)],CREAM,width=1)
    p.poly([(76,72),(95,81),(108,60),(114,72),(103,97),(80,91)],green)
    p.poly([(26,80),(18,91),(40,94)],shade)
    p.rect((38,84,74,89),rgb('#c97942'),width=1)
    p.save('goblimon')

def ogremon():
    p=Painter(); purple=rgb('#9f63ba'); plum=rgb('#654684');lilac=rgb('#d2a8e6')
    p.ell((15,116,118,126),(13,17,43,75),outline=None)
    p.poly([(39,69),(80,70),(104,100),(85,117),(35,111),(22,90)],purple)
    p.ell((41,75,85,99),lilac,outline=None)
    p.poly([(37,100),(30,122),(52,122),(64,101)],plum)
    p.poly([(72,104),(75,123),(101,120),(87,102)],plum)
    p.poly([(39,31),(47,16),(78,16),(97,30),(100,59),(88,79),(46,75),(31,57)],purple)
    p.poly([(44,28),(38,5),(60,21)],CREAM)
    p.poly([(75,24),(96,3),(90,39)],CREAM)
    p.poly([(37,35),(20,26),(29,52)],purple)
    p.poly([(92,32),(111,26),(103,51)],purple)
    p.eye(77,42,angry=True)
    p.poly([(57,60),(89,60),(82,70),(63,68)],rgb('#4b294f'),width=2)
    for x in (62,76,85):p.poly([(x,62),(x+4,62),(x+1,70)],CREAM,width=1)
    p.poly([(29,79),(17,86),(25,103),(45,94)],purple)
    p.poly([(83,78),(107,78),(116,58),(123,65),(120,97),(91,103)],purple)
    p.line([(118,30),(116,110)],rgb('#d1b491'),9)
    p.line([(117,30),(116,110)],INK,2)
    p.ell((104,22,127,42),CREAM,width=2)
    p.rect((34,89,82,94),rgb('#a35454'),width=2)
    p.save('ogremon')

def devimon():
    p=Painter();black=rgb('#3b315d'); shadow=rgb('#1c1d3d');purple=rgb('#8c68ac');rose=rgb('#e35176')
    p.ell((14,117,115,126),(13,16,38,80),outline=None)
    p.poly([(50,70),(28,41),(8,33),(17,63),(7,86),(38,95),(54,107)],black)
    p.poly([(78,70),(103,37),(121,26),(116,69),(124,91),(93,97),(71,104)],black)
    for pts in [[(31,51),(38,70),(26,77)],[(102,47),(92,67),(107,77)]]:p.poly(pts,purple,width=2)
    p.poly([(47,66),(85,65),(92,115),(72,120),(36,114)],shadow)
    p.poly([(52,78),(73,78),(71,107),(47,104)],purple,width=2)
    p.poly([(42,99),(30,123),(53,122),(64,105)],black)
    p.poly([(75,100),(76,121),(103,122),(85,104)],black)
    p.poly([(47,22),(67,16),(88,25),(90,50),(81,76),(50,69),(40,49)],black)
    p.poly([(43,33),(30,3),(58,19)],black)
    p.poly([(78,20),(93,0),(94,36)],black)
    p.poly([(48,45),(58,42),(63,48),(57,52)],rose)
    p.poly([(72,44),(82,42),(88,48),(77,53)],rose)
    p.line([(53,60),(67,67),(80,60)],rgb('#baa0d9'),2)
    p.poly([(40,78),(17,86),(24,102),(50,92)],black)
    p.poly([(86,78),(107,84),(103,104),(79,95)],black)
    for x in [25,105]:p.poly([(x-9,94),(x,102),(x+10,91)],rgb('#aca6c5'),width=2)
    p.spark(99,18,rose)
    p.save('devimon')

def piedmon():
    p=Painter();magenta=rgb('#ab4d96');purple=rgb('#594077');white=rgb('#faf1e8');red=rgb('#d54a6e');gold=rgb('#f7cc78')
    p.ell((16,116,113,125),(13,16,43,85),outline=None)
    p.poly([(51,67),(21,69),(15,111),(38,121),(57,104)],purple)
    p.poly([(80,66),(110,74),(120,112),(91,121),(76,100)],purple)
    p.poly([(45,70),(78,68),(95,106),(80,114),(42,111),(31,96)],magenta)
    p.rect((44,106,63,122),white,width=2)
    p.rect((72,104,91,121),white,width=2)
    for x in [44,72]:p.poly([(x,120),(x+22,119),(x+19,125)],red,width=1)
    p.poly([(44,25),(85,25),(95,50),(85,75),(44,73),(33,52)],white)
    p.ell((45,42,86,66),white,width=2)
    p.ell((52,46,60,53),red,outline=None)
    p.ell((73,46,81,53),red,outline=None)
    p.ell((62,55,68,61),red,outline=None)
    p.line([(55,64),(65,68),(79,64)],INK,2)
    p.poly([(38,33),(37,7),(53,16),(62,3),(70,16),(92,7),(95,36),(79,38),(64,31),(52,39)],purple)
    for x,y in [(41,10),(62,5),(91,10)]:p.ell((x-3,y-3,x+3,y+3),gold,width=1)
    p.poly([(33,79),(16,68),(8,87),(37,103)],magenta)
    p.poly([(93,82),(112,67),(122,82),(97,108)],magenta)
    p.line([(9,48),(28,89)],rgb('#d8d9e0'),4)
    p.poly([(5,39),(12,31),(20,50),(9,58)],rgb('#e7d8ac'),width=2)
    p.line([(118,50),(100,92)],rgb('#d8d9e0'),4)
    p.poly([(117,37),(123,46),(118,61),(109,49)],rgb('#e7d8ac'),width=2)
    p.save('piedmon')

# Fondos originales dibujados en resolución reducida para pixel art.
def background(name,palette,seed):
    rnd=random.Random(seed); w,h=414,226
    img=Image.new('RGB',(w,h),palette['sky']);d=ImageDraw.Draw(img)
    # Gradiente pixelado, ligero, por franjas.
    for y in range(0,145,8):
        a=y/145; lo=palette['sky']; hi=palette['horizon']; col=tuple(int(lo[i]*(1-a)+hi[i]*a) for i in range(3));d.rectangle((0,y,w,y+8),fill=col)
    if name in ('village','forest','swamp'):
        for i in range(8):
            x=(i*67+seed*13)%440-20; y=95+(i*17)%36
            d.ellipse((x-48,y-15,x+52,y+20),fill=palette['hill'])
        d.polygon([(0,155),(75,128),(142,155),(210,123),(285,155),(343,125),(414,150),(414,226),(0,226)],fill=palette['ground'])
        for i in range(18):
            x=rnd.randrange(-8,420); y=rnd.randrange(99,202)
            if name=='village' and i%5==0:
                d.rectangle((x-10,y-1,x+9,y+26),fill=(201,161,105));d.polygon([(x-16,y),(x,y-14),(x+16,y)],fill=(120,69,86));d.rectangle((x-3,y+12,x+3,y+25),fill=(81,75,95))
            else:
                d.rectangle((x-3,y,x+4,y+32),fill=(61,63,62) if name!='forest' else (59,77,57))
                c=palette['foliage']; d.ellipse((x-22,y-15,x+22,y+12),fill=c)
                d.ellipse((x-11,y-22,x+17,y+6),fill=tuple(min(255,v+16) for v in c))
    elif name=='cave':
        d.polygon([(0,0),(70,24),(130,0),(200,30),(253,0),(321,20),(414,0),(414,226),(0,226)],fill=palette['rock'])
        d.polygon([(0,48),(57,16),(109,66),(171,24),(251,80),(304,25),(381,64),(414,20),(414,226),(0,226)],fill=palette['sky'])
        d.polygon([(0,140),(65,110),(120,153),(190,122),(240,151),(325,115),(414,139),(414,226),(0,226)],fill=palette['ground'])
        for i in range(22):
            x=rnd.randrange(414);base=rnd.randrange(150,215); tall=rnd.randrange(14,58)
            d.polygon([(x-9,base),(x+3,base-tall),(x+17,base)],fill=palette['rock'])
    elif name=='ruins':
        d.polygon([(0,149),(96,106),(188,141),(304,108),(414,145),(414,226),(0,226)],fill=palette['ground'])
        for x in [28,90,164,258,335]:
            y=121+(x%3)*7
            d.rectangle((x,y-51,x+17,y+59),fill=palette['rock']);d.rectangle((x-8,y-53,x+25,y-46),fill=palette['hill'])
            d.line([(x+3,y-20),(x+7,y+4),(x+4,y+25)],fill=palette['horizon'],width=2)
        for x,y in [(70,90),(198,119),(309,73)]:d.polygon([(x-18,y),(x,y-47),(x+17,y)],fill=palette['hill'])
    elif name=='fortress':
        d.polygon([(0,152),(50,125),(128,149),(223,104),(302,151),(414,120),(414,226),(0,226)],fill=palette['ground'])
        d.rectangle((157,52,262,173),fill=palette['rock']);d.rectangle((183,23,239,68),fill=palette['rock'])
        for x in [136,262]:d.rectangle((x,74,x+29,188),fill=palette['rock']);d.polygon([(x-8,75),(x+16,41),(x+37,75)],fill=(35,30,67))
        for x in [193,223]:d.rectangle((x,84,x+10,105),fill=(245,92,130))
        d.polygon([(191,173),(191,127),(222,127),(222,173)],fill=(25,21,46))
        for x in [0,55,110,320,370]:
            d.line([(x,225),(x+19,189),(x+41,226)],fill=palette['lava'],width=6)
    # Bright floating digital pixels.
    for i in range(45):
        x=rnd.randrange(414);y=rnd.randrange(20,208);a=rnd.choice([2,3,4]);color=palette['glow']
        if name in ('swamp','ruins','fortress','cave') and i%2==0:d.rectangle((x,y,x+a,y+a),fill=color)
        elif y<120: d.point((x,y),fill=color)
    # foreground ground plane
    d.polygon([(0,195),(77,184),(146,196),(219,180),(308,191),(414,184),(414,226),(0,226)],fill=palette['front'])
    for i in range(27):
        x=rnd.randrange(414);y=rnd.randrange(196,226)
        d.line([(x,y),(x+rnd.randrange(-6,8),y+2)],fill=palette['detail'],width=2)
    info=PngImagePlugin.PngInfo();info.add_text('Artwork','Original generated landscape for student RPG; not from Digidex.')
    img.save(BACK/f'{name}.png',pnginfo=info)

BACKGROUNDS={
 'village':dict(sky=(66,151,196),horizon=(160,215,194),hill=(92,179,150),ground=(85,143,101),foliage=(42,116,89),front=(57,117,92),detail=(145,198,123),rock=(63,113,130),glow=(237,240,177),lava=(255,176,88)),
 'forest':dict(sky=(17,69,100),horizon=(52,127,119),hill=(44,113,106),ground=(47,111,83),foliage=(34,99,65),front=(24,80,66),detail=(92,160,119),rock=(67,106,94),glow=(139,242,211),lava=(208,146,66)),
 'cave':dict(sky=(54,45,83),horizon=(103,76,120),hill=(74,73,118),ground=(80,70,101),foliage=(83,74,109),front=(44,41,72),detail=(136,105,157),rock=(114,93,141),glow=(224,167,242),lava=(248,139,65)),
 'swamp':dict(sky=(19,65,76),horizon=(75,111,94),hill=(47,92,83),ground=(47,83,74),foliage=(42,94,75),front=(27,71,65),detail=(101,156,116),rock=(89,96,99),glow=(117,236,198),lava=(236,151,61)),
 'ruins':dict(sky=(58,56,99),horizon=(116,91,143),hill=(116,103,153),ground=(85,78,116),foliage=(99,91,130),front=(54,54,92),detail=(133,116,169),rock=(140,129,161),glow=(220,185,252),lava=(236,151,61)),
 'fortress':dict(sky=(46,28,75),horizon=(125,52,92),hill=(109,43,71),ground=(83,40,67),foliage=(103,55,79),front=(44,29,61),detail=(150,70,95),rock=(62,46,85),glow=(255,102,164),lava=(255,102,75)),
}

def main():
    DIGI.mkdir(parents=True,exist_ok=True);BACK.mkdir(parents=True,exist_ok=True)
    for action in [hero_agumon,hero_greymon,betamon,goblimon,ogremon,devimon,piedmon]:action()
    for idx,(n,p) in enumerate(BACKGROUNDS.items()):background(n,p,idx+5)
    print('Creados 7 sprites + 6 fondos originales:',ROOT/'assets')

if __name__=='__main__':main()
