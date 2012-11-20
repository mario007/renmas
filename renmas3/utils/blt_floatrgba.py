import platform
from tdasm import Tdasm, Runtime
import renmas3.switch as proc
from renmas3.base import ImageBGRA, ImagePRGBA

#NOTE here we have tree different way how pack float r, g, b, a to b, g, r, a byte for display 
# Main difference here is that we in ssse3 have pshufb instruction for converting bytes  
# and speed diiference is big in this example
# If conversion of rgba to bgra is not necessary maybe we can avoid lot of code here
# Main reason for conversion to bgra is that windows like this format for display

def _avx_loop(esi, edi):
    code = """
    vmovaps xmm0, oword [mask]
    vmovaps xmm1, oword [scale]
    _petlja:
    """
    code += "vmovups xmm2, oword [" + esi + "]" + """
    vminps xmm2, xmm2, oword [clamp] 
    vpxor xmm6, xmm6, xmm6
    vmaxps xmm2, xmm2, xmm6
    vmulps xmm2, xmm2, xmm1
    vcvtps2dq xmm2, xmm2
    vpshufb xmm2, xmm2, xmm0
    """
    code += " vmovss dword [" + edi + "], xmm2" + """
    """
    return code

def _ssse3_loop(esi, edi):
    code = """
    movaps xmm0, oword [mask]
    movaps xmm1, oword [scale]
    _petlja:
    """
    code += "movups xmm2, oword [" + esi + "]" + """
    minps xmm2, oword [clamp] 
    pxor xmm6, xmm6
    maxps xmm2, xmm6
    mulps xmm2, xmm1
    cvtps2dq xmm2, xmm2
    pshufb xmm2, xmm0 
    """
    code += "movss dword [" + edi + "], xmm2" + """
    """
    return code

def _sse2_loop(esi, edi):
    code = """
    movaps xmm0, oword [mask]
    movaps xmm1, oword [scale]
    _petlja:
    """
    code += "movups xmm2, oword [" + esi + "]" + """
    minps xmm2, oword [clamp] 
    pxor xmm6, xmm6
    maxps xmm2, xmm6
    mulps xmm2, xmm1
    cvtps2dq xmm2, xmm2

    movaps oword [temp], xmm2
    xor eax, eax
    xor ebx, ebx
    xor edx, edx
    xor ebp, ebp
    mov eax, dword [temp + 8] ; b
    mov ebx, dword [temp + 4] ; g
    mov edx, dword [temp]     ; r
    mov ebp, dword [temp + 12]; a
    rcl ebx, 8
    rcl edx, 16
    rcl ebp, 24
    or eax, ebx
    or edx, ebp
    or eax, edx
    """
    code += "mov dword [" + edi + "], eax" + """

    """
    return code

def _loop_code():
    bits = platform.architecture()[0]
    if bits == "64bit":
        esi = " rsi "
        edi = " rdi "
    else:
        esi = " esi "
        edi = " edi "
    if proc.AVX:
        return _avx_loop(esi, edi)
    else:
        if proc.SSSE3:
            return _ssse3_loop(esi, edi)
        else:
            return _sse2_loop(esi, edi)

def _blt_floatrgba_code32():
    code = """
        #DATA
        uint32 sa, da, dx4, sx16, sy, sw
        uint32 y, y2, spitch, dpitch
        float scale[4] = 255.9, 255.9, 255.9, 255.9
        uint8 mask[16] = 8, 4, 0, 12, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80
        float clamp[4] = 0.99, 0.99, 0.99, 0.99
        float temp[4] ; fo

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
    """
    code += _loop_code() + """
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
    return code

def _blt_floatrgba_code64():
    code = """
        #DATA
        uint64 sa, da
        uint32 dx4, sx16, sy, sw

        uint32 y, y2, spitch, dpitch
        float scale[4] = 255.9, 255.9, 255.9, 255.9
        uint8 mask[16] = 8, 4, 0, 12, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80
        float clamp[4] = 0.99, 0.99, 0.99, 0.99
        float temp[4] 

        #CODE
        call _bltrgba
        #END

        _bltrgba:
        mov eax, dword [y]
        cmp eax, dword [y2]
        je _endblt
        imul eax, dword [dpitch]
        add eax, dword [dx4]
        add rax, qword [da]
        mov rdi, rax
        mov rsi, qword [sa]
        mov eax, dword [spitch]
        imul eax, dword [sy]
        add rsi, rax
        mov ebx, dword [sx16]
        add rsi, rbx
        mov ecx, dword [sw]

        ;rep movs dword [edi], dword [esi]
    """
    code += _loop_code() + """
        add rsi, 16
        add rdi, 4
        sub ecx, 1
        jnz _petlja
        
        add dword [sy], 1
        add dword [y], 1
        jmp _bltrgba
        _endblt:
        ret 
    """ 
    return code

def _blt_floatrgba_code():
    bits = platform.architecture()[0]
    if bits == '64bit':
        return _blt_floatrgba_code64()
    else:
        return _blt_floatrgba_code32()

_mc = Tdasm().assemble(_blt_floatrgba_code())
_runtime = Runtime()
_data_section = _runtime.load("bltfloatrgba", _mc)

# blt float rgba to byte bgra
def blt_floatbgra(src, dest):

    assert isinstance(src, ImagePRGBA)
    assert isinstance(dest, ImageBGRA)

    sa, spitch = src.address_info() 
    da, dpitch = dest.address_info()
    dx = dy = sx = sy = 0
    sw, sh = src.size()

    ds = _data_section
    ds["da"] = da
    ds["sa"] = sa
    ds["dx4"] = dx * 4
    ds["sx16"] = sx * 16
    ds["sy"] = sy
    ds["spitch"] = spitch
    ds["dpitch"] = dpitch
    ds["y"] = dy
    ds["y2"] = dy + sh
    ds["sw"] = sw
    _runtime.run("bltfloatrgba")
    return True

