from PIL import Image
W=H=32
PAL={'o':(50,40,60),'p':(244,152,170),'P':(212,110,136),'w':(255,250,245),'W':(230,220,222),
 'c':(146,138,160),'k':(60,50,72),'e':(34,26,46),'h':(255,255,255),'b':(255,172,190),
 'g':(160,152,176),'G':(128,119,146),'l':(204,198,214),'L':(84,74,96),'a':(255,240,245),'A':(240,190,206)}
def ell(cx,cy,rx,ry,w=40,h=40):
    return {(x,y) for x in range(-4,w) for y in range(-4,h) if ((x+.5-cx)/rx)**2+((y+.5-cy)/ry)**2<=1}
def ring(s): return {(x+dx,y+dy) for x,y in s for dx,dy in((1,0),(-1,0),(0,1),(0,-1))}-s
ARROW=[
"o......",
"oo.....",
"oao....",
"oaao...",
"oaaao..",
"oaaaao.",
"oaaaaao",
"oaaoooo",
"oao....",
"oo.....",
"o......",
]
TAILS=[[(20,13),(21,13),(22,13),(23,12),(24,11),(24,10),(23,9),(22,9),(22,10)],
       [(20,13),(21,13),(22,13),(23,13),(24,12),(25,11),(25,10),(24,9),(23,9)]]
def opossum(i):
    """side view, facing up-left toward the pointer; local coords ~25x19"""
    g={}
    bob = 1 if i in (3,4) else 0           # head dips a little (sniff)
    blink = i==6
    body=ell(13.8,11.6,6.3,4.5)
    head=ell(7.5,7+bob,4.9,4.6)|ell(3.4,9.2+bob,3.2,2.3)
    legs=set()
    for lx in (8,11,14,17):
        legs|={(lx,y) for y in range(14,17)}|{(lx+1,y) for y in range(14,17)}
    tail=list(dict.fromkeys(TAILS[(i//2)%2])); tail=set(tail)
    allm=body|head|legs
    for p in ring(allm): g[p]='o'
    for p in legs: g[p]='L'
    for lx in (8,11,14,17): g[(lx,16)]='p'; g[(lx+1,16)]='p'
    for p in body: g[p]='g'
    for p in body:
        if p[1]>=14 or (p[0]>=19 and p[1]>=12): g[p]='G'
    for p in ell(13.5,13,4.5,1.6): 
        if p in body: g[p]='l'
    for p in ring(tail):
        if p not in body: g[p]='o'
    for p in tail: g[p]='p'
    for p in list(tail)[:2]: g[p]='P'
    # inner outline between head and body so the head reads in front
    for p in ring(head):
        if p in body: g[p]='o'
    for p in head: g[p]='w'
    for p in head:
        x,y=p
        if y<=4+bob and x>=5: g[p]='c'          # grey crown
        if y==5+bob and x>=8: g[p]='c'
        if y>=10+bob and x>=6: g[p]='W'         # chin shade
    # ear
    ear=ell(10.5,3+bob,2.1,2.1)
    for p in ring(ear):
        if p not in head or p[1]<=3+bob: g[p]='o'
    for p in ear: g[p]='k'
    g[(10,3+bob)]='p'
    # eye (big, kawaii)
    ex,ey=6,6+bob
    if blink:
        g[(ex,ey+2)]='e'; g[(ex+1,ey+2)]='e'; g[(ex+2,ey+1)]='e'
    else:
        for x in (ex,ex+1,ex+2):
            for y in (ey,ey+1,ey+2): g[(x,y)]='e'
        g[(ex,ey)]='w' ; g[(ex+2,ey+2)]='w'   # round corners
        g[(ex+1,ey)]='e'; g[(ex,ey+1)]='e'
        g[(ex+1,ey+1)]='h'
    g[(9,10+bob)]="b"; g[(10,10+bob)]="b"        # blush
    # big round opossum nose (twitches on frame 3)
    ny=8+bob+(1 if i==3 else 0)
    for p in ((0,ny),(1,ny),(0,ny+1),(1,ny+1)): g[p]='p'
    g[(1,ny)]='h' if i!=3 else 'p'
    g[(0,ny+1)]='P'
    for p in ((-1,ny),(-1,ny+1),(0,ny-1),(1,ny-1),(0,ny+2)): g[p]='o'
    g[(3,11+bob)]='o'; g[(4,11+bob)]='o'   # little mouth
    return g
def frame(i):
    img=Image.new('RGBA',(W,H),(0,0,0,0))
    g=opossum(i); ox,oy=4,7
    for (x,y),c in g.items():
        X,Y=x+ox,y+oy
        if 0<=X<W and 0<=Y<H: img.putpixel((X,Y),PAL[c]+(255,))
    for y,r in enumerate(ARROW):
        for x,ch in enumerate(r):
            if ch!='.': img.putpixel((x,y),PAL[ch]+(255,))
    sh=[(1,2),(1,3),(1,4),(1,5),(1,6),(1,7),(1,8),(1,8)][i]
    img.putpixel(sh,PAL['h']+(255,))
    return img
def halo(img):
    a=img.split()[3]; out=Image.new('RGBA',img.size,(0,0,0,0))
    for y in range(H):
        for x in range(W):
            if not a.getpixel((x,y)) and any(0<=x+dx<W and 0<=y+dy<H and a.getpixel((x+dx,y+dy)) for dx,dy in((1,0),(-1,0),(0,1),(0,-1))):
                out.putpixel((x,y),(255,250,248,235))
    out.alpha_composite(img); return out
frames=[halo(frame(i)) for i in range(8)]
