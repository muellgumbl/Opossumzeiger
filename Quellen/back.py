import math, sys
sys.path.insert(0,'.')
from side import PAL, ell, ring, halo, W, H
from PIL import Image
PAL=dict(PAL); PAL.update({'z':(150,140,190),'r':(236,120,150),'R':(255,236,240)})
def opossum_back(i, mood):
    """lying on its back, legs up. mood: 'dead' or 'sleep'"""
    g={}
    breathe = mood=='sleep' and i%8 in (2,3,4,5)
    body=ell(13.5,11.2-(0.4 if breathe else 0),7.4,4.0+(0.4 if breathe else 0))
    head=ell(5.8,11.6,4.6,4.1)|ell(2.0,12.6,2.6,2.0)
    legs=set(); feet=set()
    twitch = mood=='dead' and i in (3,4)
    for k,lx in enumerate((8,11,15,18)):
        top=4 if not (twitch and k==2) else 3
        if mood=='sleep': top=5 if k%2==0 else 6        # relaxed, bent paws
        legs|={(lx,y) for y in range(top,9)}|{(lx+1,y) for y in range(top,9)}
        feet|={(lx,top),(lx+1,top)}
    tail=[(21,13),(22,13),(23,12),(24,11),(24,10),(23,9),(22,9),(22,10)]
    if mood=='sleep' and i%8>=4: tail=[(21,13),(22,13),(23,13),(24,12),(25,11),(25,10),(24,9),(23,9)]
    tail=set(tail)
    allm=body|head|legs
    for p in ring(allm): g[p]='o'
    for p in legs: g[p]='L'
    for p in feet: g[p]='p'
    for p in body: g[p]='g'
    for p in body:
        if p[1]<=10: g[p]='l'          # belly up
        if p[1]>=14: g[p]='G'
    for p in ring(tail):
        if p not in body: g[p]='o'
    for p in tail: g[p]='p'
    for p in ring(head):
        if p in body: g[p]='o'
    for p in head: g[p]='w'
    for p in head:
        if p[1]>=14 and p[0]>=4: g[p]='c'        # crown is at the bottom now
    ear=ell(8.3,15.6,1.9,1.7)
    for p in ring(ear):
        if p not in head or p[1]>=15: g[p]='o'
    for p in ear: g[p]='k'
    g[(8,16)]='p'
    # face
    if mood=='dead':
        for p in ((4,10),(6,10),(5,11),(4,12),(6,12)): g[p]='e'      # X eye
        g[(1,15)]='p'; g[(2,15)]='p'; g[(1,16)]='P'                    # tongue out
        for p in ((0,15),(3,15),(0,16),(2,16),(1,17)): g[p]='o'
    else:
        for p in ((4,11),(5,12),(6,12),(7,11)): g[p]='e'                # happy closed eye
    g[(7,13)]='b'; g[(8,13)]='b'
    # nose
    for p in ((-1,11),(0,11),(-1,12),(0,12)): g[p]='p'
    g[(-1,12)]='P'
    for p in ((-2,11),(-2,12),(-1,10),(0,10),(-1,13)): g[p]='o'
    return g
NOSIGN=[
"..ooooo..",
".oRRRRRo.",
"oRroooroRo"[:9],
"oRo.oroRo",
"oRo.rr.oRo"[:9],
"oRo.r..oRo"[:9],
]
def nosign():
    s={}
    for x in range(11):
        for y in range(11):
            cx,cy=x+.5-5.5,y+.5-5.5; d=math.hypot(cx,cy)
            if d<=5.5:
                if d>4.8: s[(x,y)]='o'
                elif d>3.7: s[(x,y)]='r'
                elif abs(cx-cy)<=0.75: s[(x,y)]='r'     # slash top-left -> bottom-right
                else: s[(x,y)]='R'
    return s
def frame_noallowed(i):
    img=Image.new('RGBA',(W,H),(0,0,0,0))
    for (x,y),c in opossum_back(i,'dead').items():
        X,Y=x+7,y+12
        if 0<=X<W and 0<=Y<H: img.putpixel((X,Y),PAL[c]+(255,))
    for (x,y),c in nosign().items(): img.putpixel((x,y),PAL[c]+(255,))
    return img
def frame_busy(i):
    import spin
    img=Image.new('RGBA',(W,H),(0,0,0,0))
    for (x,y),c in opossum_back(i//2,'sleep').items():
        X,Y=x+6,y+11
        if 0<=X<W and 0<=Y<H: img.putpixel((X,Y),PAL[c]+(255,))
    # two z's floating up
    Zb=["####","..#.",".#..","####"]; Zs=["###",".#.","###"]
    Zs=["###","..#",".#.","###"][:0] or ["##","#.","##"][:0] or None
    def putz(pat,x0,y0):
        for yy,row in enumerate(pat):
            for xx,ch in enumerate(row):
                if ch=='#' and 0<=y0+yy<H: img.putpixel((x0+xx,y0+yy),PAL['z']+(255,))
    ph=(i//2)%8
    putz(Zb,25,8-ph//2)
    if False: putz(["###",".#.","###"] if False else ["###","..#","###"][:0] or ["##.",".#.",".##"],29,6-(ph-3)//2)
    fill,border=spin.arrow_px(i)
    for (x,y) in border: img.putpixel((x,y),PAL['o']+(255,))
    for (x,y),c in fill.items(): img.putpixel((x,y),spin.COL[c]+(255,))
    return img
