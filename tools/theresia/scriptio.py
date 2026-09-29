"""Theresia script text: slice extraction, translation encoding and adv/txt rebuild."""
import struct, hashlib
from lib import *

def slice_file(adv, txt):
    """Partition txt into parts: list of dict(off,L,refs,kind). refs = [(pos,size)] adv record positions."""
    acc,gaps,sup=resolve(adv,txt)
    parts=[]
    for (off,L),refs in acc.items():
        parts.append(dict(off=off,L=L,kind='ref',refs=[(x[0],x[2]) for x in refs]))
    for a,b in gaps:
        parts.append(dict(off=a,L=b-a,kind='raw',refs=[]))
    parts.sort(key=lambda p:p['off'])
    # sanity: disjoint & complete
    pos=0
    for p in parts:
        assert p['off']==pos,(p['off'],pos)
        pos+=p['L']
    assert pos==len(txt)
    return parts

def unit_text(txt, part):
    """Source text as unicode (cp932) so the fullwidth punctuation survives."""
    return bytes(txt[part['off']:part['off']+part['L']]).decode('cp932')

def unit_id(s):
    return hashlib.sha1(s.encode('utf-8')).hexdigest()[:12]

def rebuild(adv, txt, parts, new_bytes):
    """new_bytes: list aligned with parts -> bytes for each part. Returns (adv2, txt2)."""
    adv2=bytearray(adv); out=bytearray()
    for p,nb in zip(p_iter(parts),new_bytes):
        off2=len(out); out+=nb
        if p['kind']=='ref':
            L2=len(nb)
            assert 0<L2<=127,(L2,nb)
            for pos,size in p['refs']:
                if size==7:
                    adv2[pos+2]=L2; struct.pack_into('<I',adv2,pos+3,off2)
                else:
                    adv2[pos+1]=L2; struct.pack_into('<I',adv2,pos+2,off2)
    return bytes(adv2),bytes(out)
def p_iter(parts): return parts
