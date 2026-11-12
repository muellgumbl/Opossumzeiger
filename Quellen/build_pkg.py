"""Builds the Windows (.cur/.ani + install.inf) and GNOME (Xcursor) packages from allset.ALL"""
import sys, os, io, struct, shutil, tarfile
sys.path.insert(0,'/home/claude/cur3')
from allset import ALL
from PIL import Image

OUT='/home/claude/pkg/Opossum_Zeiger'
shutil.rmtree(OUT, ignore_errors=True)
WIN=f'{OUT}/Windows'; os.makedirs(WIN)

def scaled(img, px):
    if px==32: return img
    if px%32==0: return img.resize((px,px), Image.NEAREST)
    big=img.resize((96,96), Image.NEAREST)          # 48 px: nearest from 96
    return big.resize((px,px), Image.NEAREST)
def hs_scaled(hs, px):
    s=px/32
    return (min(px-1,int(hs[0]*s)), min(px-1,int(hs[1]*s)))

# ---------- Windows ----------
def cur_bytes(img, hs, sizes=(32,48,64,96)):
    blobs=[]
    for px in sizes:
        b=io.BytesIO(); scaled(img,px).save(b,'PNG'); blobs.append((px,hs_scaled(hs,px),b.getvalue()))
    head=struct.pack('<HHH',0,2,len(blobs))
    off=6+16*len(blobs); entries=b''; data=b''
    for px,(hx,hy),blob in blobs:
        entries+=struct.pack('<BBBBHHII',px%256,px%256,0,0,hx,hy,len(blob),off+len(data))
        data+=blob
    return head+entries+data
def chunk(cid, body):
    return cid+struct.pack('<I',len(body))+body+(b'\0' if len(body)%2 else b'')
def ani_bytes(frames, ms, hs):
    jif=max(1,round(ms*60/1000))
    anih=struct.pack('<9I',36,len(frames),len(frames),0,0,0,0,jif,1)   # AF_ICON
    icons=b''.join(chunk(b'icon',cur_bytes(f,hs)) for f in frames)
    body=b'ACON'+chunk(b'anih',anih)+chunk(b'LIST',b'fram'+icons)
    return b'RIFF'+struct.pack('<I',len(body))+body

winfile={}
for key,(frames,ms,hs,label) in ALL.items():
    if len(frames)>1:
        name=f'{key}.ani'; data=ani_bytes(frames,ms,hs)
    else:
        name=f'{key}.cur'; data=cur_bytes(frames[0],hs)
    open(f'{WIN}/{name}','wb').write(data); winfile[key]=name

# Windows 10/11 role order of the scheme string
ROLES=[('Arrow','normal'),('Help','hilfe'),('AppStarting','hintergrund'),('Wait','beschaeftigt'),
       ('Crosshair','fadenkreuz'),('IBeam','text'),('NWPen','handschrift'),('No','nicht_verfuegbar'),
       ('SizeNS','resize_ns'),('SizeWE','resize_ew'),('SizeNWSE','resize_nwse'),('SizeNESW','resize_nesw'),
       ('SizeAll','verschieben_kreuz'),('UpArrow','pfeil_hoch'),('Hand','link'),('Pin','ort'),('Person','person')]
crlf='\r\n'
inf=[ '; Opossum-Mauszeiger fuer Windows 10/11',
 '; Rechtsklick -> Installieren (Windows 11: "Weitere Optionen anzeigen" -> Installieren)',
 '[Version]','signature="$CHICAGO$"','',
 '[DefaultInstall]','CopyFiles = Scheme.Cur','AddReg = Scheme.Reg','',
 '[DestinationDirs]','Scheme.Cur = 10,"%CUR_DIR%"','',
 '[Scheme.Reg]',
 'HKCU,"Control Panel\\Cursors\\Schemes","%SCHEME_NAME%",0x00020000,"'+','.join(f'%10%\\%CUR_DIR%\\%{k}%' for _,k in ROLES)+'"',
 'HKCU,"Control Panel\\Cursors",,0x00020000,"%SCHEME_NAME%"']
inf+= [f'HKCU,"Control Panel\\Cursors","{role}",0x00020000,"%10%\\%CUR_DIR%\\%{k}%"' for role,k in ROLES]
inf+= ['','[Scheme.Cur]']+sorted(set(winfile.values()))
inf+= ['','[Strings]','CUR_DIR = "Cursors\\Opossum"','SCHEME_NAME = "Opossum"']
inf+= [f'{k} = "{winfile[k]}"' for _,k in ROLES]
open(f'{WIN}/install.inf','w',newline='').write(crlf.join(inf)+crlf)

open(f'{WIN}/LIESMICH.txt','w',newline='').write(crlf.join([
'Opossum-Mauszeiger fuer Windows 10/11','',
'Installieren:',
' 1. Ordner entpacken (nicht direkt aus der Zip-Datei heraus starten).',
' 2. Rechtsklick auf install.inf -> "Installieren".',
'    Windows 11: Rechtsklick -> "Weitere Optionen anzeigen" -> "Installieren".',
' 3. Einstellungen -> Bluetooth und Geraete -> Maus -> "Weitere Mauseinstellungen"',
'    -> Reiter "Zeiger" -> Schema "Opossum" waehlen -> "Uebernehmen".','',
'Groesse: Die Zeiger enthalten 32, 48, 64 und 96 px. Windows waehlt passend zur',
'Bildschirmskalierung. Groesser: Einstellungen -> Barrierefreiheit -> Mauszeiger und Toucheingabe.','',
'Entfernen: Im Reiter "Zeiger" ein anderes Schema waehlen, "Opossum" markieren -> "Loeschen".',
'Die Dateien liegen unter C:\\Windows\\Cursors\\Opossum.','',
'Extras ohne Windows-Rolle (nur GNOME nutzt sie, koennen aber manuell zugewiesen werden):',
' '+', '.join(sorted(v for k,v in winfile.items() if k not in dict((b,a) for a,b in ROLES))),'']))

# ---------- GNOME / Xcursor ----------
THEME='Opossum'; GN=f'{OUT}/GNOME'; TD=f'/home/claude/pkg/theme/{THEME}'
shutil.rmtree('/home/claude/pkg/theme',ignore_errors=True); os.makedirs(f'{TD}/cursors')
NOMINAL={24:32, 48:64, 96:96}     # nominal size -> image pixels (only integer scaling)
def xcursor_bytes(frames, ms, hs):
    images=[]
    for nom,px in NOMINAL.items():
        for f in frames:
            im=scaled(f,px).convert('RGBA'); hx,hy=hs_scaled(hs,px)
            pix=bytearray()
            for r,g,b,a in im.getdata():
                pix+=struct.pack('<I',(a<<24)|((r*a//255)<<16)|((g*a//255)<<8)|(b*a//255))
            hdr=struct.pack('<9I',36,0xfffd0002,nom,1,px,px,hx,hy,ms if len(frames)>1 else 0)
            images.append((nom,hdr+bytes(pix)))
    n=len(images); pos=16+12*n; toc=b''; data=b''
    for nom,blob in images:
        toc+=struct.pack('<III',0xfffd0002,nom,pos+len(data)); data+=blob
    return b'Xcur'+struct.pack('<III',16,0x10000,n)+toc+data

PRIMARY={  # freedesktop name -> our cursor
 'default':'normal','help':'hilfe','progress':'hintergrund','wait':'beschaeftigt','crosshair':'fadenkreuz',
 'text':'text','vertical-text':'text','pencil':'handschrift','not-allowed':'nicht_verfuegbar',
 'pointer':'link','grab':'verschieben','grabbing':'greifen','dnd-ask':'dnd_frage','copy':'kopieren',
 'alias':'alias','context-menu':'kontextmenue','zoom-in':'zoom_plus','zoom-out':'zoom_minus',
 'ns-resize':'resize_ns','ew-resize':'resize_ew','nwse-resize':'resize_nwse','nesw-resize':'resize_nesw',
 'move':'verschieben_kreuz','up-arrow':'pfeil_hoch','person':'person','pin':'ort','text-tail':'text_schwanz'}
LINKS={
 'default':['left_ptr','arrow','top_left_arrow','left_arrow'],
 'help':['question_arrow','whats_this','left_ptr_help','5c6cd98b3f3ebcb1f9c7f1c204630408','d9ce0ab605698f320427677b458ad60b'],
 'progress':['left_ptr_watch','half-busy','3ecb610c1bf2410f44200f48c40d3599','00000000000000020006000e7e9ffc3f','08e8e1c95fe2fc01f976f1e063a24ccd'],
 'wait':['watch'],
 'crosshair':['cross','tcross','cross_reverse','diamond_cross','cell','plus'],
 'text':['xterm','ibeam'],
 'pencil':['draft','draft_large','draft_small'],
 'not-allowed':['no-drop','dnd-no-drop','dnd-none','crossed_circle','forbidden','circle','pirate','X_cursor','03b6e0fcb3499374a867c041f52298f0'],
 'pointer':['hand','hand1','hand2','pointing_hand','e29285e634086352946a0e7090d73106','9d800788f1b08800ae810202380a0822'],
 'grab':['openhand','5aca4d189052212118709018842178c0','9141b49c8149039304290b508d208c40'],
 'grabbing':['closedhand','dnd-move','dnd-none-closed','fcf21c00b30f7e3f83fe0dfd12e71cff','208530c400c041818281048008011002'],
 'dnd-ask':['dnd-question','question'],
 'copy':['dnd-copy','1081e37283d90000800003c07f3ef6bf','6407b0e94181790501fd1e167b474872','08ffe1cb5fe6fc01f906f1c063814ccf'],
 'alias':['link','dnd-link','3085a0e285430894940527032f8b26df','640fb0e74195791501fd1ed57b41487f','0876e1c15ff2fc01f906f1c363074c0f'],
 'ns-resize':['size_ver','sb_v_double_arrow','v_double_arrow','n-resize','s-resize','row-resize','top_side','bottom_side','double_arrow','split_v','00008160000006810000408080010102','2870a09082c103050810ffdffffe0204'],
 'ew-resize':['size_hor','sb_h_double_arrow','h_double_arrow','e-resize','w-resize','col-resize','left_side','right_side','split_h','028006030e0e7ebffc7f7070c0600140','14fef782d02440884392942c11205230'],
 'nwse-resize':['size_fdiag','nw-resize','se-resize','top_left_corner','bottom_right_corner','bd_double_arrow','c7088f0f3e6c8088236ef8e1e3e70000'],
 'nesw-resize':['size_bdiag','ne-resize','sw-resize','top_right_corner','bottom_left_corner','fd_double_arrow','fcf1c3c7cd4491d801f1e1c78f100000'],
 'move':['fleur','all-scroll','size_all','4498f0e0c1937ffe01fd06f973665830','9081237383d90e509aa00f00170e968f'],
 'up-arrow':['center_ptr','sb_up_arrow'],
}
for name,key in PRIMARY.items():
    frames,ms,hs,_=ALL[key]
    open(f'{TD}/cursors/{name}','wb').write(xcursor_bytes(frames,ms,hs))
nlinks=0
for name,aliases in LINKS.items():
    for a in aliases:
        p=f'{TD}/cursors/{a}'
        if not os.path.lexists(p): os.symlink(name,p); nlinks+=1
open(f'{TD}/index.theme','w').write('[Icon Theme]\nName=Opossum\nComment=Niedliche Pixel-Opossum-Mauszeiger\nInherits=Adwaita\n')
os.makedirs(GN)
with tarfile.open(f'{GN}/Opossum-Cursor-Theme.tar.gz','w:gz') as t: t.add(TD, arcname=THEME)
open(f'{GN}/install_gnome.sh','w').write('''#!/usr/bin/env bash
# Installiert das Opossum-Mauszeiger-Theme fuer den aktuellen Benutzer und aktiviert es.
set -euo pipefail
cd "$(dirname "$0")"
DEST="$HOME/.local/share/icons"
mkdir -p "$DEST"
rm -rf "$DEST/Opossum"
tar -xzf Opossum-Cursor-Theme.tar.gz -C "$DEST"
# auch unter ~/.icons verlinken, damit aeltere X11-Programme es finden
mkdir -p "$HOME/.icons"; ln -sfn "$DEST/Opossum" "$HOME/.icons/Opossum"
gsettings set org.gnome.desktop.interface cursor-theme 'Opossum'
echo "Opossum-Zeiger aktiviert. Groesse aendern: gsettings set org.gnome.desktop.interface cursor-size 48"
echo "Falls einzelne Programme noch alte Zeiger zeigen: einmal ab- und wieder anmelden."
''')
os.chmod(f'{GN}/install_gnome.sh',0o755)
open(f'{GN}/uninstall_gnome.sh','w').write('''#!/usr/bin/env bash
set -euo pipefail
gsettings reset org.gnome.desktop.interface cursor-theme
rm -rf "$HOME/.local/share/icons/Opossum"; rm -f "$HOME/.icons/Opossum"
echo "Opossum-Zeiger entfernt, Standardzeiger wiederhergestellt."
''')
os.chmod(f'{GN}/uninstall_gnome.sh',0o755)
print('windows files:',len(winfile),' xcursors:',len(PRIMARY),' links:',nlinks)
