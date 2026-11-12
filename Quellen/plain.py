import math, sys
sys.path.insert(0,'.')
import spin
from side import ell, ring, halo, W, H
from PIL import Image
O=(50,40,60); L=(255,255,255); M=(252,214,228); A=(234,150,182); D=(190,96,134)
C={'o':O,'L':L,'M':M,'A':A,'D':D,'p':(244,152,170)}
def cone(tip, ang, Lc=7.0, w=3.2):
    """flat-shaded cone, tip at `tip`, pointing in direction ang (radians, screen coords)."""
    tx,ty=tip; ux,uy=-math.cos(ang),-math.sin(ang)   # axis from tip backwards
    nx,ny=-uy,ux
    inside={}
    for x in range(W):
        for y in range(H):
            px,py=x+.5-(tx+.5),y+.5-(ty+.5)
            t=px*ux+py*uy; c=px*nx+py*ny
            if 0<=t<=Lc and abs(c)<=w*t/Lc+0.45:
                inside[(x,y)]='L' if c>0.6 else ('A' if c<-0.6 else 'M')
    return inside
def shaft(p0,p1,width=1.0):
    (x0,y0),(x1,y1)=p0,p1; s={}
    n=int(max(abs(x1-x0),abs(y1-y0))*2)+1
    for k in range(n+1):
        x=x0+(x1-x0)*k/n; y=y0+(y1-y0)*k/n
        for dx in range(-1,2):
            for dy in range(-1,2):
                X,Y=round(x+dx*0.5),round(y+dy*0.5)
                if math.hypot(X-x,Y-y)<=width: s[(X,Y)]='M'
    return s
def render(shapes):
    allin={}
    for s in shapes: allin.update(s)
    border={p for p in allin if any((p[0]+dx,p[1]+dy) not in allin for dx,dy in((1,0),(-1,0),(0,1),(0,-1)))}
    img=Image.new('RGBA',(W,H),(0,0,0,0))
    for p,c in allin.items():
        if 0<=p[0]<W and 0<=p[1]<H: img.putpixel(p,(O if p in border else C[c])+(255,))
    return halo(img)
def resize(direction):
    c=15.5
    v={'ns':(0,1),'ew':(1,0),'nwse':(1,1),'nesw':(1,-1)}[direction]
    n=math.hypot(*v); vx,vy=v[0]/n,v[1]/n
    R=12.5
    t1=(round(c-vx*R-.5),round(c-vy*R-.5)); t2=(round(c+vx*R-.5),round(c+vy*R-.5))
    a1=math.atan2(-vy,-vx); a2=math.atan2(vy,vx)
    return render([shaft((c-.5-vx*6,c-.5-vy*6),(c-.5+vx*6,c-.5+vy*6)),cone(t1,a1),cone(t2,a2)])
def move():
    c=15
    shapes=[shaft((c,6),(c,24)),shaft((6,c),(24,c))]
    shapes+= [cone((c,2),-math.pi/2),cone((c,28),math.pi/2),cone((2,c),math.pi),cone((28,c),0)]
    img=render(shapes)
    for p in ((14,14),(15,14),(14,15),(15,15),(16,15),(15,16)): img.putpixel(p,C['p']+(255,))
    return img
def cross():
    img=Image.new('RGBA',(W,H),(0,0,0,0))
    for k in range(3,13):
        for p in ((15,k),(15,30-k),(k,15),(30-k,15)): img.putpixel(p,O+(255,))
    for p in ((15,15),):
        img.putpixel(p,C['p']+(255,))
    for p in ((14,14),(16,14),(14,16),(16,16)): img.putpixel(p,(244,152,170,140))
    return halo(img)
def text(tail=False):
    img=Image.new('RGBA',(W,H),(0,0,0,0))
    for y in range(8,24): img.putpixel((15,y),O+(255,))
    for x in (12,13,14,16,17,18):
        img.putpixel((x,7),O+(255,)); img.putpixel((x,24),O+(255,))
    img.putpixel((15,7),O+(255,)); img.putpixel((15,24),O+(255,))
    for x in (13,17): img.putpixel((x,7),C['p']+(255,)); img.putpixel((x,24),C['p']+(255,))
    if tail:   # curly opossum tail hanging from the I-beam
        for p in ((16,25),(17,26),(18,27),(19,27),(20,26),(20,25),(19,24),(18,25)):
            img.putpixel(p,C['p']+(255,))
    return halo(img)
PLAIN={'text':text(),'text_schwanz':text(True),'fadenkreuz':cross(),'resize_ns':resize('ns'),'resize_ew':resize('ew'),
       'resize_nwse':resize('nwse'),'resize_nesw':resize('nesw'),'verschieben_kreuz':move()}
