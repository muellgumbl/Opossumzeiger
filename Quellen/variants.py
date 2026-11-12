import math, sys
sys.path.insert(0,'.')
import spin, lying, back
from side import PAL as SPAL, ell, ring, halo, W, H
from PIL import Image
PAL=dict(back.PAL); PAL.update(lying.PAL); PAL.update(back.PAL)
def blit(img, g, ox, oy, pal=PAL):
    for (x,y),c in g.items():
        X,Y=x+ox,y+oy
        if 0<=X<W and 0<=Y<H: img.putpixel((X,Y),pal[c]+(255,))
def glyph(pat, ch='r'):
    g={}
    fill={(x,y) for y,row in enumerate(pat) for x,c in enumerate(row) if c=='#'}
    for p in ring(fill): g[p]='o'
    for p in fill: g[p]=ch
    return g
QMARK=[".###.","##.##","...##","..##.","..#..",".....","..#.."]
def seated(img,i,ox=5,oy=9):
    blit(img, spin.opossum(i), ox, oy)
def arrow(img,i):
    fill,border=spin.arrow_px(i)
    for p in border: img.putpixel(p,PAL['o']+(255,))
    for p,c in fill.items(): img.putpixel(p,spin.COL[c]+(255,))

# --- Hilfe: drehender Pfeil + wippendes rosa "?"
def help_frame(i):
    img=Image.new('RGBA',(W,H),(0,0,0,0))
    seated(img,i//2)
    bob=[0,0,-1,-1,-1,0,0,1][(i//2)%8]
    blit(img, glyph(QMARK), 15, 1+bob)
    arrow(img,i)
    return img

# --- Zoom: Lupe (Hotspot = Linsenmitte 5,5) + schnupperndes Opossum
def lens(sign):
    g={}
    for x in range(11):
        for y in range(11):
            d=math.hypot(x+.5-5.5,y+.5-5.5)
            if d<=5.3: g[(x,y)]='o' if d>4.4 else ('r' if d>3.4 else 'R')
    for k in range(3,8): g[(k,5)]='P'
    if sign=='+':
        for k in range(3,8): g[(5,k)]='P'
    for k in range(0,2):                 # handle
        for p in ((9+k,10+k),(10+k,10+k),(10+k,9+k)): g[p]='o' if p!=(10+k,10+k) else 'k'
    return g
def zoom_frame(i,sign):
    img=Image.new('RGBA',(W,H),(0,0,0,0))
    seated(img,i,ox=6,oy=11)
    blit(img, lens(sign), 0, 0)
    return img

# --- Pfoten: offen (Verschieben) und greifend (grabbing)
def paw(open_=True):
    fingers = {0:(2,6),1:(0,6),2:(1,6),3:(3,6)} if open_ else {0:(4,6),1:(3,6),2:(3,6),3:(4,6)}
    m=set()
    for k,(top,bot) in fingers.items():
        x0=3+k*3
        m|={(x,y) for x in (x0,x0+1) for y in range(top,bot+1)}
    palm={(x,y) for x in range(3,14) for y in range(6,12)}
    palm-= {(3,11),(13,11)}
    thumb={(1,7),(2,7),(1,8),(2,8),(2,9)} if open_ else {(2,8),(3,8),(2,9)}
    m|=palm|thumb
    g={}
    for p in ring(m): g[p]='o'
    for p in m: g[p]='p'
    for p in m:
        if p[1]>=10: g[p]='P'
    for k in range(4):
        x0=3+k*3; top=fingers[k][0]
        g[(x0,top)]='a'
        if not open_: g[(x0,6)]='o'; g[(x0+1,6)]='o' if k<3 else 'p'
    return g
def paw_frame(i, open_=True, q=False):
    img=Image.new('RGBA',(W,H),(0,0,0,0))
    blit(img, lying.opossum_lying(i), 5, 9)
    blit(img, paw(open_), -1, 0)
    if q:
        bob=[0,0,-1,-1,-1,0,0,1][i%8]
        blit(img, glyph(QMARK), 13, 4+bob)
    return img
def dnd_frame(i):
    img=Image.new('RGBA',(W,H),(0,0,0,0))
    blit(img, lying.opossum_lying(i), 5, 8)
    for (x,y),c in [((x,y),ch) for y,r in enumerate(lying.PAW) for x,ch in enumerate(r) if ch!='.']:
        img.putpixel((x,y),PAL[c]+(255,))
    bob=[0,0,-1,-1,-1,0,0,1][i%8]
    blit(img, glyph(QMARK), 13, 2+bob)
    return img
SETS={
 'hilfe':      ([halo(help_frame(i)) for i in range(16)],117),
 'zoom_plus':  ([halo(zoom_frame(i,'+')) for i in range(8)],150),
 'zoom_minus': ([halo(zoom_frame(i,'-')) for i in range(8)],150),
 'dnd_frage':  ([halo(dnd_frame(i)) for i in range(8)],150),
 'verschieben':([halo(paw_frame(i,True)) for i in range(8)],150),
 'greifen':    ([halo(paw_frame(i,False)) for i in range(8)],150),
}
