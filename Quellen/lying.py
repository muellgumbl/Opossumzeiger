import math, sys
sys.path.insert(0,'.')
from side import PAL, ell, ring, halo, W, H
from PIL import Image
PAL=dict(PAL); PAL.update({'a':(255,214,226),'p':(244,152,170),'P':(212,110,136),'n':(230,128,150)})
# pointing opossum paw, hotspot = fingertip (2,0)
PAW=[
"..oo.......",
".oapo......",
".oapo......",
".oapoooooo.",
".oapopopopo",
"ooapppppppo",
"oaapppppppo",
"oapppppppPo",
".oappppppPo",
"..oPPPPPPo.",
"...oooooo..",
]
TAILS=[[(21,11),(22,10),(23,9),(23,8),(23,7),(22,6),(21,6),(21,7)],
       [(21,11),(22,10),(23,10),(24,9),(24,8),(24,7),(23,6),(22,6)],
       [(21,11),(22,10),(23,9),(23,8),(23,7),(22,6),(21,6),(21,7)],
       [(21,11),(21,10),(22,9),(22,8),(21,7),(20,6),(19,6),(19,7)]]
def opossum_lying(i):
    g={}
    blink = i==5
    hb = 1 if i in (2,3) else 0          # head rests / lifts slightly
    body=ell(14.5,12.6,7.2,3.6)
    head=ell(7,10.2+hb*0.5,4.7,4.2)|ell(3,12+hb*0.5,3.0,2.2)
    kick = i in (2,3,6,7)
    back=ell(21.8,13.4,1.8,1.2) if kick else ell(21.5,14.6,1.8,1.2)   # back foot kicks
    tail=set(TAILS[i%4])
    allm=body|head|back
    for p in ring(allm): g[p]='o'
    for p in body: g[p]='g'
    for p in body:
        if p[1]>=15: g[p]='G'
    for p in back: g[p]='p'
    for p in ring(tail):
        if p not in body: g[p]='o'
    for p in tail: g[p]='p'
    for p in ring(head):
        if p in body: g[p]='o'
    for p in head: g[p]='w'
    for p in head:
        x,y=p
        if y<=7 and x>=5: g[p]='c'
        if y>=13 and x>=5: g[p]='W'
    ear=ell(10.5,6.4,2.0,2.0)
    for p in ring(ear):
        if p not in head or p[1]<=6: g[p]='o'
    for p in ear: g[p]='k'
    g[(10,6)]='p'
    # eye
    ex,ey=6,9
    if blink:
        g[(ex,ey+2)]='e'; g[(ex+1,ey+2)]='e'; g[(ex+2,ey+1)]='e'
    else:
        for x in (ex,ex+1,ex+2):
            for y in (ey,ey+1,ey+2): g[(x,y)]='e'
        g[(ex,ey)]='w'; g[(ex+2,ey+2)]='w'; g[(ex+1,ey+1)]='h'
    g[(9,13)]='b'; g[(10,13)]='b'
    # nose
    ny=11
    for p in ((0,ny),(1,ny),(0,ny+1),(1,ny+1)): g[p]='p'
    g[(1,ny)]='h'; g[(0,ny+1)]='P'
    for p in ((-1,ny),(-1,ny+1),(0,ny-1),(1,ny-1),(0,ny+2)): g[p]='o'
    # front paws under the chin
    for px in (3,6):
        for p in ((px,15),(px+1,15)): g[p]='p'
        for p in ((px-1,15),(px+2,15),(px,16),(px+1,16)): g[p]='o'
    return g
def frame(i, ox=5, oy=8):
    img=Image.new('RGBA',(W,H),(0,0,0,0))
    for (x,y),c in opossum_lying(i).items():
        X,Y=x+ox,y+oy
        if 0<=X<W and 0<=Y<H: img.putpixel((X,Y),PAL[c]+(255,))
    wig = 1 if i in (1,2,5,6) else 0   # paw taps (finger wiggle) without moving hotspot
    for y,r in enumerate(PAW):
        for x,ch in enumerate(r):
            if ch!='.': img.putpixel((x,y),PAL[ch]+(255,))
    return img
frames=[halo(frame(i)) for i in range(8)]
