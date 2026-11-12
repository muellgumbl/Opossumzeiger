import math, sys
sys.path.insert(0,'.')
import spin
from variants import PAL, blit as _blit, glyph, seated, arrow
from side import ell, ring, halo, W, H
from PIL import Image
PAL=dict(PAL); PAL.update({'S':(226,60,84),'s':(250,110,120),'v':(96,170,90),'V':(60,120,70),'y':(255,226,140),
  't':(150,156,168),'T':(112,118,132),'u':(188,194,204),'m':(255,255,255),'n':(120,110,130)})
def blit(img,g,ox,oy): _blit(img,g,ox,oy,PAL)
def strawberry(bite=0):
    pat=[".vVv.","sSSSs","SSySS","SsSSS",".SyS.","..S.."]
    g={}
    m={(x,y) for y,r in enumerate(pat) for x,c in enumerate(r) if c!='.'}
    if bite: m-={(0,1),(0,2)} if bite==1 else {(0,1),(0,2),(1,1)}
    for p in ring(m): g[p]='o'
    for (x,y) in m: g[(x,y)]=pat[y][x]
    return g
def appstarting(i):
    img=Image.new('RGBA',(W,H),(0,0,0,0))
    seated(img,i//2)
    k=(i//2)%8
    blit(img, strawberry(bite=(k//3)%3), 1, 19+(1 if k in (2,3) else 0))
    arrow(img,i); return img
def baby():
    g={}
    body=ell(6,5,3.8,2.6); head=ell(2.4,4,2.6,2.4)
    for p in ring(body|head): g[p]='o'
    for p in body: g[p]='g'
    for p in body:
        if p[1]>=6: g[p]='G'
    for p in ring(head):
        if p in body: g[p]='o'
    for p in head: g[p]='w'
    for p in head:
        if p[1]<=2: g[p]='c'
    g[(2,3)]='e'; g[(2,4)]='e'; g[(-1,4)]='p'; g[(0,4)]='p'; g[(4,5)]='b'
    for p in ((3,0),(4,0),(3,1)): g[p]='k'
    for p in ((10,4),(11,3),(11,2),(10,1)): g[p]='p'
    return g
def person(i):
    img=Image.new('RGBA',(W,H),(0,0,0,0))
    seated(img,i//2)
    blit(img, baby(), 15, 9+(1 if (i//2)%8 in (3,4) else 0))
    arrow(img,i); return img
def pin():
    g={}
    head=ell(3,3,3,3)
    for p in ring(head): g[p]='o'
    for p in head: g[p]='r'
    g[(2,2)]='R'; g[(2,1)]='R'
    for y in range(6,10): g[(3,y)]='n'
    for y in range(6,10): g[(2,y)]='o'; g[(4,y)]='o'
    g[(3,10)]='o'
    return g
def location(i):
    img=Image.new('RGBA',(W,H),(0,0,0,0))
    seated(img,i//2)
    blit(img, pin(), 22, 2+(-1 if (i//2)%8 in (2,3,4) else 0))
    arrow(img,i); return img
def pencil():
    """pencil, tip (hotspot) at (0,0), body going down-right"""
    g={}
    for k in range(1,10):
        for d in (-1,0,1):
            p=(k+d if d>0 else k, k-d if d<0 else k) if False else None
    body=set()
    for k in range(2,8):
        body|={(k,k),(k+1,k),(k,k+1)}
    for p in ring(body|{(1,1)}): g[p]='o'
    for p in body: g[p]='r'
    for k in range(2,8): g[(k+1,k)]='R'
    for p in ((1,1),(2,2),(3,2),(2,3)): g[p]='y'
    g[(0,0)]='o'; g[(1,1)]='n'
    for p in ((7,7),(8,7),(7,8),(8,8)): g[p]='p'
    return g
def handwriting(i):
    img=Image.new('RGBA',(W,H),(0,0,0,0))
    seated(img,i,ox=6,oy=11)
    blit(img, pencil(), 0, 0)
    return img
def uparrow(i):
    img=Image.new('RGBA',(W,H),(0,0,0,0))
    seated(img,i,ox=5,oy=12)
    import plain
    shapes=[plain.cone((5,0),-math.pi/2,Lc=6,w=3.0), plain.shaft((5,6),(5,10))]
    allin={}
    for s in shapes: allin.update(s)
    border={p for p in allin if any((p[0]+dx,p[1]+dy) not in allin for dx,dy in((1,0),(-1,0),(0,1),(0,-1)))}
    for p,c in allin.items(): img.putpixel(p,(plain.O if p in border else plain.C[c])+(255,))
    return img
# --- trash can family (copy / alias / context menu)
def can():
    g={}
    m={(x,y) for x in range(0,13) for y in range(0,10)}
    m-={(0,9),(12,9)}
    for p in ring(m): g[p]='o'
    for p in m: g[p]='t'
    for x in range(0,13): g[(x,0)]='u'; g[(x,1)]='u'
    for x in (3,6,9):
        for y in range(3,9): g[(x,y)]='T'
    for x in range(-1,14): g[(x,2)]='o'
    return g
def can_frame(i, badge):
    img=Image.new('RGBA',(W,H),(0,0,0,0))
    peek=[0,0,-1,-1,-1,0,0,0][(i//2)%8]
    seated(img,i//2,ox=10,oy=9+peek)
    blit(img, can(), 15, 21)
    if badge=='copy':
        g={}
        disk=ell(4,4,4,4)
        for p in ring(disk): g[p]='o'
        for p in disk: g[p]='m'
        for k in range(2,7): g[(k,4)]='r'; g[(4,k)]='r'
        g[(3,4)]='r'
        blit(img,g,3,22)
    elif badge=='alias':
        tail=[(6,1),(5,0),(4,0),(3,1),(2,2),(2,3),(2,4),(3,5),(4,6),(5,6),(6,6),(7,5)]
        g={}
        for p in ring(set(tail)): g[p]='o'
        for p in tail: g[p]='p'
        for p in ((6,4),(8,4),(7,6),(8,6),(8,5)): g[p]='p'
        for p in ((5,3),(9,3),(9,7),(6,7)): g.setdefault(p,'o')
        blit(img,g,3,22)
    elif badge=='menu':
        g={}
        m={(x,y) for x in range(0,8) for y in range(0,9)}
        for p in ring(m): g[p]='o'
        for p in m: g[p]='m'
        for y in (2,4,6):
            for x in range(1,7): g[(x,y)]='r' if y==2 else 'n'
        blit(img,g,3,21)
    arrow(img,i); return img
EXTRAS={
 'hintergrund':([halo(appstarting(i)) for i in range(16)],117),
 'person':     ([halo(person(i)) for i in range(16)],117),
 'ort':        ([halo(location(i)) for i in range(16)],117),
 'handschrift':([halo(handwriting(i)) for i in range(8)],150),
 'pfeil_hoch': ([halo(uparrow(i)) for i in range(8)],150),
 'kopieren':   ([halo(can_frame(i,'copy')) for i in range(16)],117),
 'alias':      ([halo(can_frame(i,'alias')) for i in range(16)],117),
 'kontextmenue':([halo(can_frame(i,'menu')) for i in range(16)],117),
}
