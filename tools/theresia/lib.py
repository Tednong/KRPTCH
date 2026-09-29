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

def all_refs(adv,txt):
    out=[]
    for i in range(len(adv)-6):
        if adv[i] in (0x10,0x14,0x84) and adv[i+1]==0:
            L=adv[i+2]; off=struct.unpack_from('<I',adv,i+3)[0]
            if 0<L<=127 and off+L<=len(txt) and printable(txt[off:off+L]): out.append((i,adv[i],7,L,off))
    for i in range(len(adv)-5):
        if adv[i] in (0x1c,0xf2):
            L=adv[i+1]; off=struct.unpack_from('<I',adv,i+2)[0]
            if 0<L<=127 and off+L<=len(txt) and printable(txt[off:off+L]): out.append((i,adv[i],6,L,off))
    return out

def resolve(adv,txt):
    """Accepted disjoint refs {(off,L): [(adv_pos,op,size)]}, plus unresolved gaps."""
    rf=all_refs(adv,txt)
    by_pos={x[0]:x for x in rf}
    sup={}
    for x in rf:
        i,op,sz,L,off=x; c=0
        for d in (6,7,8,9):
            for j in (i+d,i-d):
                y=by_pos.get(j)
                if y and (y[4]==off+L or y[4]+y[3]==off): c+=1
        sup[i]=c
    groups={}
    for x in rf: groups.setdefault((x[4],x[3]),[]).append(x)
    def gs(k): return max(sup[x[0]] for x in groups[k])
    occ=bytearray(len(txt)); accepted={}
    def free(off,L): return not any(occ[off:off+L])
    # phase 1: chain-supported, best support first then longer
    for k in sorted([k for k in groups if gs(k)>0 and k[1]>=2],key=lambda k:(-gs(k),-k[1],k)):
        if free(*k):
            accepted[k]=groups[k]
            for q in range(k[0],k[0]+k[1]): occ[q]=1
    # phase 2: unsupported refs must be free and touch an accepted edge; longest first, repeat
    rest=sorted([k for k in groups if k not in accepted and k[1]>=2],key=lambda k:(-k[1],k))
    n=len(txt); changed=True
    while changed:
        changed=False
        for k in rest:
            if k in accepted: continue
            a,b=k[0],k[0]+k[1]
            if any(occ[a:b]): continue
            if (a==0 or occ[a-1]) or (b==n or occ[b]):
                accepted[k]=groups[k]
                for q in range(a,b): occ[q]=1
                changed=True
    gaps=[];s0=None
    for q,c in enumerate(occ):
        if not c and s0 is None: s0=q
        if c and s0 is not None: gaps.append((s0,q)); s0=None
    if s0 is not None: gaps.append((s0,len(occ)))
    return accepted,gaps,sup
