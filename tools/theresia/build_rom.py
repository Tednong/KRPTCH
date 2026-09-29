#!/usr/bin/env python3
"""Build a Korean-patched Theresia (USA) ROM from the user's own ROM.

usage: build_rom.py INPUT.nds OUTPUT.nds [--work DIR]
Needs: python3, ndspy, Pillow. Reads translations/theresia/ko.tsv, tools/theresia/fonts/Galmuri11.ttf.
The source ROM is never modified or copied into the repository.
"""
import sys, os, re, json, hashlib, struct
from PIL import Image, ImageDraw, ImageFont
import ndspy.rom, ndspy.lz10
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE)
os.environ.setdefault('THERESIA_ROM','')
import trlib, nftr
from scriptio import slice_file, unit_text, rebuild
import lib

HANGUL=re.compile(r'[가-힣]')
SRC_SHA1='55c846e3eacef50e89e54f226da782d9875f1622'
STORE=os.path.join(HERE,'..','..','translations','theresia','ko.tsv')
FONT_TTF=os.path.join(HERE,'fonts','Galmuri11.ttf')
HANGUL_W=12
KO_LEAD=list(range(0x88,0xA0))+list(range(0xE0,0xEB))
KO_TRAIL=list(range(0x40,0x7F))+list(range(0x80,0xFD))

def load_store():
    d={}
    for line in open(STORE,encoding='utf-8'):
        line=line.rstrip('\n')
        if line:
            k,v=line.split('\t',1); d[k]=v
    return d
def bh(body): return hashlib.sha1(body.encode('utf-8')).hexdigest()[:12]

def allocate_codes(chars):
    codes={}; it=((l<<8)|t for l in KO_LEAD for t in KO_TRAIL)
    for ch in sorted(chars): codes[ch]=next(it)
    return codes

def encode(ko, codes):
    out=bytearray()
    for ch in ko:
        o=ord(ch)
        if o<128: out.append(o)
        elif ch in codes: out+=struct.pack('>H',codes[ch])
        else: out+=ch.encode('cp932')
    return bytes(out)

def render_glyphs(chars, codes):
    f=ImageFont.truetype(FONT_TTF,12)
    glyphs=[];widths=[];cmap={}
    for i,ch in enumerate(sorted(chars)):
        im=Image.new('L',(15,16),0); d=ImageDraw.Draw(im); d.fontmode='1'
        d.text((0,2),ch,font=f,fill=255)
        rows=[[3 if im.getpixel((x,y)) else 0 for x in range(15)] for y in range(16)]
        glyphs.append(nftr.pack_glyph(rows,15,16)); widths.append((0,HANGUL_W,HANGUL_W))
        cmap[codes[ch]]=i
    return glyphs,widths,cmap

def main(src,dst):
    r=ndspy.rom.NintendoDSRom.fromFile(src)
    sha=hashlib.sha1(open(src,'rb').read()).hexdigest()
    if sha!=SRC_SHA1: print('WARNING: input ROM SHA-1 %s differs from the supported one (%s)'%(sha,SRC_SHA1))
    store=load_store()
    # pass 1: collect used syllables
    chars=set(); plans={}
    for n in lib.scripts(r):
        adv,txt=lib.get(r,n); parts=slice_file(adv,txt); new=[]
        for p in parts:
            raw=bytes(txt[p['off']:p['off']+p['L']])
            if p['kind']!='ref': new.append(None); continue
            s=raw.decode('cp932'); pre,body,suf=trlib.split_unit(s)
            ko=store.get(bh(body)) if body.strip() else None
            if ko is not None: chars.update(c for c in ko if HANGUL.match(c))
            new.append((pre,ko,suf))
        plans[n]=(adv,txt,parts,new)
    codes=allocate_codes(chars)
    # font
    font=nftr.Nftr(ndspy.lz10.decompress(bytes(r.getFileByName('data/a.NFTR'))))
    glyphs,widths,cmap=render_glyphs(chars,codes)
    fnt=nftr.build(font,glyphs,widths,cmap)
    r.setFileByName('data/a.NFTR',ndspy.lz10.compress(fnt))
    # scripts
    stats=[0,0]
    for n,(adv,txt,parts,new) in plans.items():
        nb=[]
        for p,pl in zip(parts,new):
            raw=bytes(txt[p['off']:p['off']+p['L']])
            if pl is None or pl[1] is None: nb.append(raw); stats[1]+=1; continue
            pre,ko,suf=pl
            b=pre.encode('cp932')+encode(ko,codes)+suf.encode('cp932'); nb.append(b); stats[0]+=1
        adv2,txt2=rebuild(adv,txt,parts,nb)
        r.setFileByName(n+'.adv',ndspy.lz10.compress(adv2)); r.setFileByName(n+'.txt',ndspy.lz10.compress(txt2))
    r.saveToFile(dst)
    print('translated units: %d, untranslated (kept English): %d, hangul glyphs: %d'%(stats[0],stats[1],len(chars)))
    json.dump({format(v,'04X'):k for k,v in codes.items()},open(dst+'.charmap.json','w'),ensure_ascii=False)
if __name__=='__main__':
    main(sys.argv[1],sys.argv[2])
