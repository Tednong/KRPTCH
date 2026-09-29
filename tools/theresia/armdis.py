import ndspy.rom, struct, sys
from capstone import *
r=ndspy.rom.NintendoDSRom.fromFile(__import__('os').environ.get('THERESIA_ROM','theresia.nds'))
a9=bytes(r.arm9); base=0x2000000
md=Cs(CS_ARCH_ARM, CS_MODE_ARM)
def lit(addr): return struct.unpack_from('<I',a9,addr-base)[0]
def dis(lo,hi):
    for ins in md.disasm(a9[lo-base:hi-base], lo):
        s=f"{ins.address:x}: {ins.mnemonic} {ins.op_str}"
        if ins.mnemonic=='ldr' and ins.op_str.startswith('r') and '[pc, #' in ins.op_str:
            imm=int(ins.op_str.split('#')[1].rstrip(']'),16); a=ins.address+8+imm
            s+=f"   ; ={lit(a):#x}"
        print(s)
if __name__=='__main__':
    dis(int(sys.argv[1],16),int(sys.argv[2],16))
