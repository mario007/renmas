
import x86
from tdasm import Tdasm, Runtime

MEMCPY = """
    #DATA
    uint32 sa, da, n

    #CODE
    call _memcpy 

    #END
    
    _memcpy:
    mov ecx, dword [n]
    mov esi, dword [sa] 
    mov edi, dword [da]
    rep movs dword [edi], dword [esi]

    ret
"""

BLTRGBA = """
    #DATA
    uint32 sa, da, dx4, sx4, sy, sw

    uint32 y, y2, spitch, dpitch


    #CODE
    call _bltrgba

    #END

    _bltrgba:

    mov eax, dword [y]
    cmp eax, dword [y2]
    je _endblt
    imul eax, dword [dpitch]
    add eax, dword [dx4]
    add eax, dword [da]
    mov edi, eax
    mov esi, dword [sa]
    mov eax, dword [spitch]
    imul eax, dword [sy]
    add esi, eax
    add esi, dword [sx4]
    mov ecx, dword [sw]
    rep movs dword [edi], dword [esi]
    
    
    add dword [sy], 1
    add dword [y], 1
    jmp _bltrgba
    _endblt:
    ret 

"""

BLTFLOATRGBA = """
    #DATA
    uint32 sa, da, dx4, sx16, sy, sw

    uint32 y, y2, spitch, dpitch
    float scale[4] = 255.9, 255.9, 255.9, 255.9
    uint8 mask[16] = 8, 4, 0, 12, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80

    #CODE
    call _bltrgba

    #END

    _bltrgba:

    mov eax, dword [y]
    cmp eax, dword [y2]
    je _endblt
    imul eax, dword [dpitch]
    add eax, dword [dx4]
    add eax, dword [da]
    mov edi, eax
    mov esi, dword [sa]
    mov eax, dword [spitch]
    imul eax, dword [sy]
    add esi, eax
    add esi, dword [sx16]
    mov ecx, dword [sw]


    ;rep movs dword [edi], dword [esi]
    movaps xmm0, oword [mask]
    movaps xmm1, oword [scale]
    _petlja:

    movups xmm2, oword [esi]
    mulps xmm2, xmm1
    cvtps2dq xmm2, xmm2
    pshufb xmm2, xmm0 
    movss dword [edi], xmm2

    add esi, 16
    add edi, 4
    sub ecx, 1
    jnz _petlja
    
    add dword [sy], 1
    add dword [y], 1
    jmp _bltrgba
    _endblt:
    ret 

"""

#FIXME repari blitter dw, dh????
class Blitter:
    def __init__(self):
        asm = Tdasm()
        m = asm.assemble(MEMCPY)
        self.r = Runtime()
        self.ds = self.r.load("memcpy", m)
        m2 = asm.assemble(BLTRGBA)
        self.ds2 = self.r.load("bltrgba", m2)
        m3 = asm.assemble(BLTFLOATRGBA)
        self.ds3 = self.r.load("bltfloatrgba", m3)

    def blt_rgba(self, da, dx, dy, dw, dh, dpitch, sa, sx, sy, sw, sh, spitch):
        if dx < 0 or dx > dw: return None
        if dy < 0 or dy > dh: return None

        if sw > dw - dx: sw = dw - dx
        if sh > dh - dy: sh = dh - dy

        self.ds2["da"] = da
        self.ds2["sa"] = sa
        self.ds2["dx4"] = dx * 4
        self.ds2["sx4"] = sx * 4
        self.ds2["sy"] = sy
        self.ds2["spitch"] = spitch
        self.ds2["dpitch"] = dpitch
        self.ds2["y"] = dy
        self.ds2["y2"] = dy + sh
        self.ds2["sw"] = sw
        self.r.run("bltrgba")

        #for j in range(dy, dy+sh):
        #    self._memcpy(da + j * dpitch + dx*4, sa + sy * spitch + sx*4, sw)
        #    sy += 1

    def _memcpy(self, da, sa, n):
        self.ds["da"] = da
        self.ds["sa"] = sa
        self.ds["n"] = n
        
        self.r.run("memcpy")

        #ints = x86.GetUInt32(sa, 0, n)
        #x86.SetUInt32(da, ints, 0)
        
    def _convFloatToInt(self, arr):
        lst = []
        #pix = (a<<24) | (r<<16) | (g<<8) | b
        for x in range(0, len(arr), 4):
            a = int(arr[x] * 256.0)
            r = int(arr[x + 1] * 256.0)
            g = int(arr[x + 2] * 256.0)
            b = int(arr[x + 3] * 256.0)
            pix = (a<<24) | (r<<16) | (g<<8) | b
            lst.append(pix)
        return tuple(lst)
            
    def blt_floatTorgba(self, da, dx, dy, dw, dh, dpitch, sa, sx, sy, sw, sh, spitch):
        if dx < 0 or dx > dw: return None
        if dy < 0 or dy > dh: return None

        if sw > dw - dx: sw = dw - dx
        if sh > dh - dy: sh = dh - dy

        self.ds3["da"] = da
        self.ds3["sa"] = sa
        self.ds3["dx4"] = dx * 4
        self.ds3["sx16"] = sx * 16
        self.ds3["sy"] = sy
        self.ds3["spitch"] = spitch
        self.ds3["dpitch"] = dpitch
        self.ds3["y"] = dy
        self.ds3["y2"] = dy + sh
        self.ds3["sw"] = sw
        self.r.run("bltfloatrgba")
 
        #for j in range(dy, dy+sh):
        #    dest = da + j * dpitch + dx*4
        #    source = sa + sy * spitch + sx*16
        #    
        #    stup = x86.GetFloat(source, 0, sw * 4)
        #    ret = self._convFloatToInt(stup)
        #    x86.SetUInt32(dest, ret, 0)
        #    sy += 1

