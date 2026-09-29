import ndspy.rom, ndspy.lz10, struct
import os
ROM=os.environ.get('THERESIA_ROM','theresia.nds')
def load():
    return ndspy.rom.NintendoDSRom.fromFile(ROM)
def scripts(r):
    def walk(f,p=''):
        for n in f.files: yield p+n
        for n,sub in f.folders: yield from walk(sub,p+n+'/')
    return [n[:-4] for n in walk(r.filenames) if n.startswith('data/script/') and n.endswith('.txt.adv')]
def get(r,n):
    return ndspy.lz10.decompress(bytes(r.getFileByName(n+'.adv'))), ndspy.lz10.decompress(bytes(r.getFileByName(n+'.txt')))
def rec(adv,i):
    if i+7<=len(adv) and adv[i]==0x14 and adv[i+1]==0: return adv[i+2], struct.unpack_from('<I',adv,i+3)[0]
def chain_records(adv):
    recs=[]
    n=len(adv)
    for i in range(n-7):
        a=rec(adv,i)
        if not a: continue
        L,off=a
        ok=False
        j=i+7
        if j<n and adv[j]==0x11: j+=1
        b=rec(adv,j)
        if b and b[1]==off+L: ok=True
        # prev
        for pj in (i-7,i-8):
            p=rec(adv,pj) if pj>=0 else None
            if p and off==p[1]+p[0]: ok=True
        if ok: recs.append((i,L,off))
    return recs

OPS={0x10,0x14,0x84}
def printable(b): return len(b)>0 and all(32<=c<127 or c>=0x80 for c in b)
def candidates(adv,txt):
    d={}
    for i in range(len(adv)-6):
        if adv[i] in OPS and adv[i+1]==0:
            L=adv[i+2]; off=struct.unpack_from('<I',adv,i+3)[0]
            if 0<L<=127 and off+L<=len(txt) and printable(txt[off:off+L]): d[i]=(adv[i],L,off)
    return d
def partition(adv,txt):
    d=candidates(adv,txt)
    # confidence: chain neighbours
    conf={}
    for i,(op,L,off) in d.items():
        c=0
        for j in (i+7,i+8,i+9):
            if j in d and d[j][2]==off+L: c+=1
        for j in (i-7,i-8,i-9):
            if j in d and off==d[j][2]+d[j][1]: c+=1
        conf[i]=c
    iv={}
    for i,(op,L,off) in d.items():
        iv.setdefault((off,L),[]).append(i)
    return d,conf,iv
