import math, sys
sys.path.insert(0,'.')
import side
from side import *
COL={'L':(255,255,255),'M':(250,214,226),'D':(214,150,176)}
COL.update({'L':(255,255,255),'M':(252,214,228),'A':(234,150,182),'D':(190,96,134)})
def arrow_px(i, L=11.8, w=4.6, d=1.3, n=16):
    """flat arrow with a centre ridge (diamond cross-section), spinning about its
    axis like the reference: goes thin twice per turn, colour bands travel across."""
    th=i*2*math.pi/n
    r2=math.sqrt(2); light=math.radians(55)
    base=[(w,0),(0,d),(-w,0),(0,-d)]
    R=[(bc*math.cos(th)-bz*math.sin(th), bc*math.sin(th)+bz*math.cos(th)) for bc,bz in base]
    faces=[]
    for k in range(4):
        (c1,z1),(c2,z2)=R[k],R[(k+1)%4]
        nc,nz=(z2-z1),-(c2-c1)
        if nc*(c1+c2)+nz*(z1+z2)<0: nc,nz=-nc,-nz
        if nz>0: faces.append((k,math.atan2(nz,nc)))
    inside={}
    for x in range(0,14):
        for y in range(0,14):
            px,py=x+.5,y+.5
            t=(px+py)/r2; c=(px-py)/r2; s_=t/L
            if not (0<t<=L): continue
            best=None
            for k,ang in faces:
                c1,c2=s_*R[k][0],s_*R[(k+1)%4][0]
                lo,hi=min(c1,c2)-0.45,max(c1,c2)+0.45
                if lo<=c<=hi:
                    mid=abs(c-(c1+c2)/2)
                    if best is None or mid<best[0]: best=(mid,ang)
            if best is None: continue
            br=math.cos(best[1]-light)
            inside[(x,y)]='L' if br>0.82 else 'M' if br>0.4 else 'A' if br>-0.05 else 'D'
    border={p for p in inside if any((p[0]+dx,p[1]+dy) not in inside for dx,dy in((1,0),(-1,0),(0,1),(0,-1)))}
    fill={p:c for p,c in inside.items() if p not in border}
    return fill, border
def frame2(i, ox=5, oy=9):
    img=Image.new('RGBA',(W,H),(0,0,0,0))
    g=opossum(i//2)
    for (x,y),c in g.items():
        X,Y=x+ox,y+oy
        if 0<=X<W and 0<=Y<H: img.putpixel((X,Y),PAL[c]+(255,))
    fill,ring=arrow_px(i)
    for (x,y) in ring:
        if 0<=x<W and 0<=y<H: img.putpixel((x,y),PAL['o']+(255,))
    for (x,y),c in fill.items(): img.putpixel((x,y),COL[c]+(255,))
    return img
frames=[halo(frame2(i)) for i in range(16)]
