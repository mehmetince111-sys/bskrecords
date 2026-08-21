# -*- coding: utf-8 -*-
"""BSK-Records-Label-Signet nach dem Tattoo: Blackletter (Old English Text MT), sanfter Bogen, enge Sterne.
Transparentes PNG (schwarz + weiss) + Preview. 3x Supersampling."""
import math, os
from PIL import Image, ImageDraw, ImageFont
FONT=r"C:\Windows\Fonts\OLDENGL.TTF"
D=r"C:\Users\memo\AppData\Local\Temp\claude\D--Clau---\12124ddd-74b5-44d9-a32b-430ff0e1af6d\scratchpad\logo"
os.makedirs(D, exist_ok=True)
SS=3
W,H=1900*SS, 1150*SS

def star(dr,cx,cy,r,fill,rot=-math.pi/2):
    pts=[]
    for i in range(10):
        ang=rot+i*math.pi/5; rr=r if i%2==0 else r*0.42
        pts.append((cx+rr*math.cos(ang), cy+rr*math.sin(ang)))
    dr.polygon(pts,fill=fill)

def arc_layout(text, font, radius, track):
    widths=[font.getlength(c) for c in text]
    adv=[w*track for w in widths]
    total=sum(adv)/radius
    angs=[]; a=-total/2
    for w in adv:
        ca=w/radius; angs.append(a+ca/2); a+=ca
    return widths, angs, total

def arc_text(base, text, font, cx, cy, radius, fill, track=0.86):
    widths, angs, _=arc_layout(text,font,radius,track)
    for c,w,mid in zip(text,widths,angs):
        bb=font.getbbox(c); cw=max(1,bb[2]-bb[0]); ch=max(1,bb[3]-bb[1]); pad=40
        ci=Image.new("RGBA",(cw+2*pad,ch+2*pad),(0,0,0,0))
        ImageDraw.Draw(ci).text((pad-bb[0],pad-bb[1]),c,font=font,fill=fill)
        rot=ci.rotate(-math.degrees(mid),expand=True,resample=Image.BICUBIC)
        x=cx+radius*math.sin(mid); y=cy-radius*math.cos(mid)
        base.alpha_composite(rot,(int(x-rot.width/2),int(y-rot.height/2)))

def build(fill, mid_word=None):
    img=Image.new("RGBA",(W,H),(0,0,0,0)); dr=ImageDraw.Draw(img)
    cx=W//2; cyc=int(H*1.75)               # gemeinsames Kreiszentrum unten -> konzentrische, sanfte Boegen
    f_bsk=ImageFont.truetype(FONT,int(340*SS))
    f_rec=ImageFont.truetype(FONT,int(158*SS))
    r_bsk=cyc-int(H*0.25); r_rec=cyc-int(H*0.48)
    # BSK
    arc_text(img,"BSK",f_bsk,cx,cyc,r_bsk,fill,track=0.82)
    if mid_word:
        arc_text(img,mid_word,ImageFont.truetype(FONT,int(215*SS)),cx,cyc,cyc-int(H*0.37),fill,track=0.84)
    # RECORDS
    arc_text(img,"RECORDS",f_rec,cx,cyc,r_rec,fill,track=0.90)
    # Sterne an den Bogen-Enden
    sr=int(30*SS)
    _,_,tb=arc_layout("BSK",f_bsk,r_bsk,0.82)
    _,_,trc=arc_layout("RECORDS",f_rec,r_rec,0.90)
    for sgn in (-1,1):
        ab=sgn*(tb/2+0.055); star(dr,cx+r_bsk*math.sin(ab),cyc-r_bsk*math.cos(ab),sr,fill)
        ar=sgn*(trc/2+0.05); star(dr,cx+r_rec*math.sin(ar),cyc-r_rec*math.cos(ar),int(sr*0.8),fill)
    bbox=img.getbbox()
    if bbox:
        pad=36*SS
        img=img.crop((max(0,bbox[0]-pad),max(0,bbox[1]-pad),min(W,bbox[2]+pad),min(H,bbox[3]+pad)))
    return img.resize((img.width//SS, img.height//SS), Image.LANCZOS)

import numpy as np
BLACK=(17,15,20,255); WHITE=(245,240,232,255)
main_k=build(BLACK); main_k.save(os.path.join(D,"bsk_logo_black.png"))
main_w=build(WHITE); main_w.save(os.path.join(D,"bsk_logo_white.png"))
herit_k=build(BLACK, mid_word="Warrior"); herit_k.save(os.path.join(D,"bsk_logo_heritage_black.png"))

def goldify(rgba):
    w,h=rgba.size; yy=np.linspace(0,1,h)[:,None]
    top=np.array([255,120,52]); bot=np.array([255,192,96])
    grad=np.repeat((top*(1-yy)+bot*yy)[:,None,:],w,axis=1).astype(np.uint8)
    out=Image.fromarray(grad,"RGB").convert("RGBA"); out.putalpha(rgba.split()[-1]); return out
main_g=goldify(main_k); main_g.save(os.path.join(D,"bsk_logo_gold.png"))
herit_g=goldify(herit_k); herit_g.save(os.path.join(D,"bsk_logo_heritage_gold.png"))

def card(bg,fg,label,wd=820,ht=580):
    c=Image.new("RGB",(wd,ht),bg); L=fg.copy(); L.thumbnail((wd-130,ht-140),Image.LANCZOS)
    c.paste(L,((wd-L.width)//2,(ht-L.height)//2),L); ImageDraw.Draw(c).text((18,14),label,fill=(155,150,145)); return c
pres=Image.new("RGB",(820*3+40,580),(18,16,20))
pres.paste(card((16,13,18),main_g,"Label-Signet — Gold"),(0,0))
pres.paste(card((16,13,18),main_w,"Label-Signet — Weiss"),(830,0))
pres.paste(card((16,13,18),herit_g,"Heritage (mit Warrior)"),(1660,0))
pres.save(os.path.join(D,"logo_present.png"))
print("fertig | main", main_k.size, "| heritage", herit_k.size)
