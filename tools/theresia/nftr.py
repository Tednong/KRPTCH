"""Minimal NFTR reader/writer (NitroSDK font) for Theresia: 2bpp glyph cells, HDWC widths, PAMC maps."""
import struct

class Nftr:
    def __init__(self, data):
        f=bytes(data); self.raw=f
        assert f[:4]==b'RTFN'
        hs=struct.unpack_from('<H',f,12)[0]
        off=hs; self.blocks={}
        while off<len(f):
            tag=f[off:off+4]; sz=struct.unpack_from('<I',f,off+4)[0]
            self.blocks.setdefault(tag,[]).append((off,sz)); off+=sz
        fo=self.blocks[b'FNIF'][0][0]
        self.finf=bytearray(f[fo+8:fo+28])
        po=self.blocks[b'PLGC'][0][0]
        self.cw,self.ch=f[po+8],f[po+9]; self.cs=struct.unpack_from('<H',f,po+10)[0]
        self.baseline,self.maxw,self.depth=f[po+12],f[po+13],f[po+14]
        n=(self.blocks[b'PLGC'][0][1]-16)//self.cs
        self.glyphs=[f[po+16+i*self.cs:po+16+(i+1)*self.cs] for i in range(n)]
        ho=self.blocks[b'HDWC'][0][0]
        first,last=struct.unpack_from('<HH',f,ho+8)
        self.widths=[tuple(f[ho+16+3*i:ho+19+3*i]) for i in range(last-first+1)]
        self.cmaps=[]
        for (o,sz) in self.blocks[b'PAMC']:
            a,b,t=struct.unpack_from('<HHH',f,o+8)
            if t==0: self.cmaps.append(('dir',a,b,struct.unpack_from('<H',f,o+20)[0]))
            elif t==1: self.cmaps.append(('tbl',a,b,[struct.unpack_from('<h',f,o+20+2*i)[0] for i in range(b-a+1)]))
            else:
                n2=struct.unpack_from('<H',f,o+20)[0]
                self.cmaps.append(('scan',a,b,[struct.unpack_from('<Hh',f,o+22+4*i) for i in range(n2)]))
    def code_to_glyph(self):
        m={}
        for c in self.cmaps:
            if c[0]=='dir':
                for k in range(c[2]-c[1]+1): m[c[1]+k]=c[3]+k
            elif c[0]=='tbl':
                for k,g in enumerate(c[3]):
                    if g>=0: m[c[1]+k]=g
            else:
                for code,g in c[3]: m[code]=g
        return m
    def glyph_pixels(self,idx):
        g=self.glyphs[idx]; bits=[]
        for byte in g:
            for s in (6,4,2,0): bits.append((byte>>s)&3)
        return [bits[y*self.cw:(y+1)*self.cw] for y in range(self.ch)]

def pack_glyph(rows,cw,ch):
    bits=[v for row in rows for v in row[:cw]]
    bits+= [0]*(cw*ch-len(bits))
    out=bytearray()
    for i in range(0,len(bits),4):
        q=bits[i:i+4]+[0]*(4-len(bits[i:i+4]))
        out.append((q[0]<<6)|(q[1]<<4)|(q[2]<<2)|q[3])
    return bytes(out)

def build(font, extra_glyphs, extra_widths, extra_codes):
    """Return NFTR bytes = original glyphs + extra ones; extra_codes: {sjis_code: local extra index}."""
    glyphs=list(font.glyphs)+list(extra_glyphs); widths=list(font.widths)+list(extra_widths)
    n0=len(font.glyphs)
    nglyph=len(glyphs)
    pglc=bytearray(b'PLGC'+b'\0'*4)
    pglc+=bytes([font.cw,font.ch])+struct.pack('<H',font.cs)+bytes([font.baseline,font.maxw,font.depth,0])
    for g in glyphs: pglc+=g
    while len(pglc)%4: pglc+=b'\0'
    struct.pack_into('<I',pglc,4,len(pglc))
    hdwc=bytearray(b'HDWC'+b'\0'*4)+struct.pack('<HHI',0,nglyph-1,0)
    for w in widths: hdwc+=bytes([w[0]&0xff,w[1]&0xff,w[2]&0xff])
    while len(hdwc)%4: hdwc+=b'\0'
    struct.pack_into('<I',hdwc,4,len(hdwc))
    # keep original maps except scan map, which gets the new entries too
    maps=[]
    for c in font.cmaps:
        if c[0]=='scan':
            entries=list(c[3])+[(code,n0+i) for code,i in sorted(extra_codes.items())]
            entries.sort()
            maps.append(('scan',entries))
        else: maps.append(c)
    body=b''
    blocks=[]
    for m in maps:
        if m[0]=='tbl':
            b=bytearray(b'PAMC'+b'\0'*4+struct.pack('<HHHHI',m[1],m[2],1,0,0))
            for g in m[3]: b+=struct.pack('<h',g)
        elif m[0]=='dir':
            b=bytearray(b'PAMC'+b'\0'*4+struct.pack('<HHHHI',m[1],m[2],0,0,0)+struct.pack('<H',m[3]))
        else:
            ent=m[1]
            b=bytearray(b'PAMC'+b'\0'*4+struct.pack('<HHHHI',0,0xFFFF,2,0,0)+struct.pack('<H',len(ent)))
            for code,g in ent: b+=struct.pack('<Hh',code,g)
        while len(b)%4: b+=b'\0'
        struct.pack_into('<I',b,4,len(b))
        blocks.append(b)
    # header + FINF
    finf=bytearray(b'FNIF'+struct.pack('<I',28))+bytes(font.finf)
    hs=16
    pos=hs
    off_finf=pos; pos+=len(finf)
    off_pglc=pos; pos+=len(pglc)
    off_hdwc=pos; pos+=len(hdwc)
    offs=[]
    for b in blocks: offs.append(pos); pos+=len(b)
    total=pos
    # FINF pointers: pGlyph(+0x0C? ) layout: fontType,height,alter(2),width(3),encoding, ptrGLGC, ptrCWDH, ptrCMAP
    finf[8+8:8+12]=struct.pack('<I',off_pglc+8)
    finf[8+12:8+16]=struct.pack('<I',off_hdwc+8)
    finf[8+16:8+20]=struct.pack('<I',offs[0]+8)
    # link maps
    for i,b in enumerate(blocks):
        nxt=offs[i+1]+8 if i+1<len(blocks) else 0
        struct.pack_into('<I',b,16,nxt)
    struct.pack_into('<I',hdwc,12,0)
    out=bytearray(b'RTFN'+struct.pack('<HHIHH',0xFEFF,0x0101,total,hs,3+len(blocks)))
    out+=finf+pglc+hdwc
    for b in blocks: out+=b
    return bytes(out)
