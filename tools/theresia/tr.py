#!/usr/bin/env python3
"""Translation workflow: `tr.py next N` prints untranslated bodies; `tr.py apply FILE` ingests 'n<TAB>korean' lines."""
import sys, json, re, hashlib, os
from trlib import *
import nftr
HANGUL=re.compile(r'[가-힣]')
EXTRA=set('―’‘“”■○　【】・→')
CTL=re.compile(r'%[A-Za-z%]\d*')
STORE=os.path.join(REPO,'ko.tsv')
HANGUL_ADV=12
_font=None
def font():
    global _font
    if _font is None:
        _font=nftr.Nftr(open(WORK+'/a.nftr','rb').read())
        _font.map=_font.code_to_glyph()
    return _font
def px(s):
    f=font(); w=0
    s=CTL.sub('',s)
    for ch in s:
        if HANGUL.match(ch): w+=HANGUL_ADV
        elif ord(ch)<128:
            g=f.map.get(ord(ch)); w+=f.widths[g][2] if g is not None else 8
        else:
            try: c=int.from_bytes(ch.encode('cp932'),'big'); g=f.map.get(c); w+=f.widths[g][2] if g is not None else 15
            except Exception: w+=15
    return w
def h(body): return hashlib.sha1(body.encode('utf-8')).hexdigest()[:12]
def load_store():
    d={}
    if os.path.exists(STORE):
        for line in open(STORE,encoding='utf-8'):
            line=line.rstrip('\n')
            if line: k,v=line.split('\t',1); d[k]=v
    return d
def bodies(): return json.load(open(WORK+'/bodies.json'))
LINE_CAP=216
def is_label(b): return len(b)<=20 and not re.search(r'[.,!?\u2026"\u201d:;]$|\.\.\.',b)
def limit(body):
    p=px(body)
    if is_label(body): return max(int(p*1.5)+1,72)
    return max(int(p*1.10)+1,LINE_CAP)
def validate(src,ko,tokens=True):
    errs=[]
    if ko!=ko.strip(): errs.append('leading/trailing space')
    if not ko: errs.append('empty')
    if ko and not re.sub(r'[.\s]','',ko) and re.search(r'[A-Za-z]',src): errs.append('placeholder dots')
    for ch in ko:
        if not (32<=ord(ch)<127 or HANGUL.match(ch) or ch in EXTRA): errs.append('bad char %r'%ch); break
    if tokens and sorted(CTL.findall(src))!=sorted(CTL.findall(ko)): errs.append('control tokens differ %s vs %s'%(CTL.findall(src),CTL.findall(ko)))
    if not os.environ.get('NOWIDTH') and px(ko)>limit(src): errs.append('too wide %d>%d'%(px(ko),limit(src)))
    return errs
def cmd_next(n):
    st=load_store(); out=[]; cur={}
    for b in bodies():
        if h(b) not in st and b.strip():
            out.append(b)
            if len(out)>=n: break
    for i,b in enumerate(out,1):
        cur[i]=h(b); print(f"{i}\t{b}")
    json.dump({'map':cur,'src':{i:b for i,b in enumerate(out,1)}},open(WORK+'/batch.json','w'))
def cmd_apply(path,force=False):
    import collections
    B=json.load(open(WORK+'/batch.json')); st=load_store(); ok=0; bad=[]
    add=[]; seq=[]
    for line in open(path,encoding='utf-8'):
        line=line.rstrip('\n')
        if not line.strip(): continue
        parts=line.split('\t') if '\t' in line else line.split('|')
        if len(parts)>=3: n,anc,ko=parts[0].strip(),parts[1],'|'.join(parts[2:])
        else: n,ko=parts[0].strip(),parts[1]; anc=None
        if n not in B['map']: bad.append((n,'unknown id')); continue
        if anc is not None and not B['src'][n].startswith(anc):
            bad.append((n,'ANCHOR MISMATCH',B['src'][n][:12],anc)); continue
        src=B['src'][n]; errs=validate(src,ko,tokens=False)
        if errs and not force: bad.append((n,src,ko,errs)); continue
        seq.append((n,src,ko))
    # color/wait token balance: running difference must return to zero within 4 units
    D=collections.Counter(); run=[]; groups=[]
    for n,src,ko in seq:
        D.update(collections.Counter(CTL.findall(ko))); D.subtract(collections.Counter(CTL.findall(src)))
        nz=any(v!=0 for v in D.values())
        if nz:
            run.append(n)
            if len(run)>3: groups.append(list(run)); run=[]; D=collections.Counter()
        else: run=[]
    if run: groups.append(list(run))
    rejectset={n for g in groups for n in g}
    for n,src,ko in seq:
        if n in rejectset: bad.append((n,src,ko,['unbalanced control tokens'])); continue
        add.append((B['map'][n],ko)); ok+=1
    os.makedirs(os.path.dirname(STORE),exist_ok=True)
    with open(STORE,'a',encoding='utf-8') as f:
        for k,v in add: f.write(f"{k}\t{v}\n")
    got={k for k,_ in add}
    missing=[n for n in B['map'] if B['map'][n] not in got and B['map'][n] not in st]
    print('applied',ok,'rejected',len(bad),'still missing',len(missing))
    for b in bad: print('REJECT',b)
    if missing: print('missing ids',missing[:60])
def cmd_stats():
    st=load_store(); bs=bodies(); done=sum(1 for b in bs if h(b) in st); print('translated',done,'/',len(bs))
def cmd_fix(path):
    bs=bodies(); st=load_store(); add=[]
    for line in open(path,encoding='utf-8'):
        line=line.rstrip('\n')
        if not line.strip(): continue
        i,ko=line.split('|',1); i=int(i); src=bs[i]
        errs=validate(src,ko)
        if errs: print('REJECT',i,src,ko,errs); continue
        add.append((h(src),ko))
    with open(STORE,'a',encoding='utf-8') as f:
        for k,v in add: f.write(f"{k}\t{v}\n")
    print('fixed',len(add))
def cmd_fixe(path):
    bs=set(bodies()); add=[]
    for line in open(path,encoding='utf-8'):
        line=line.rstrip('\n')
        if not line.strip(): continue
        src,ko=line.split('\t',1)
        if src not in bs: print('NOSRC',src); continue
        errs=validate(src,ko)
        if errs: print('REJECT',src,ko,errs); continue
        add.append((h(src),ko))
    with open(STORE,'a',encoding='utf-8') as f:
        for k,v in add: f.write(f"{k}\t{v}\n")
    print('fixed',len(add))
def cmd_show(a,b):
    bs=bodies(); st=load_store()
    for i in range(a,b):
        print(i,'|',bs[i],'|',st.get(h(bs[i]),'-'))
if __name__=='__main__':
    c=sys.argv[1]
    if c=='next': cmd_next(int(sys.argv[2]))
    elif c=='apply': cmd_apply(sys.argv[2], len(sys.argv)>3 and sys.argv[3]=='force')
    elif c=='stats': cmd_stats()
    elif c=='fix': cmd_fix(sys.argv[2])
    elif c=='fixe': cmd_fixe(sys.argv[2])
    elif c=='show': cmd_show(int(sys.argv[2]),int(sys.argv[3]))
