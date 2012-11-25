import platform
from tdasm import Tdasm, Runtime
import renmas3.switch as proc
from renmas3.base import ImageBGRA, ImageRGBA, ImagePRGBA

def _blt_floatrgba_code32():
    code = """
        #DATA
        uint32 sa, da, dx16, sx4, sy, sw
        uint32 y, y2, spitch, dpitch
        ; scale 1/256
        float scale[4] = 0.0039, 0.0039, 0.0039, 0.0039

        #CODE
        call _bltrgba
        #END

        _bltrgba:
        mov eax, dword [y]
        cmp eax, dword [y2]
        je _endblt
        imul eax, dword [dpitch]
        add eax, dword [dx16]
        add eax, dword [da]
        mov edi, eax
        mov esi, dword [sa]
        mov eax, dword [spitch]
        imul eax, dword [sy]
        add esi, eax
        add esi, dword [sx4]
        mov ecx, dword [sw]

        ;rep movs dword [edi], dword [esi]
        _petlja:
        movss xmm0, dword [esi]
        pxor xmm1, xmm1
        punpcklbw xmm0, xmm1
        punpcklwd xmm0, xmm1
        cvtdq2ps xmm0, xmm0
        mulps xmm0, oword [scale]
        movups oword [edi], xmm0

        add esi, 4 
        add edi, 16 
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
        uint32 dx16, sx4, sy, sw

        uint32 y, y2, spitch, dpitch
        ; scale 1/256
        float scale[4] = 0.0039, 0.0039, 0.0039, 0.0039

        #CODE
        call _bltrgba
        #END

        _bltrgba:
        mov eax, dword [y]
        cmp eax, dword [y2]
        je _endblt
        imul eax, dword [dpitch]
        add eax, dword [dx16]
        add rax, qword [da]
        mov rdi, rax
        mov rsi, qword [sa]
        mov eax, dword [spitch]
        imul eax, dword [sy]
        add rsi, rax
        mov ebx, dword [sx4]
        add rsi, rbx
        mov ecx, dword [sw]

        ;rep movs dword [edi], dword [esi]
        _petlja:
        movss xmm0, dword [rsi]
        pxor xmm1, xmm1
        punpcklbw xmm0, xmm1
        punpcklwd xmm0, xmm1
        cvtdq2ps xmm0, xmm0
        mulps xmm0, oword [scale]
        movups oword [rdi], xmm0

        add rsi, 4 
        add rdi, 16 
        sub ecx, 1
        jnz _petlja
        
        add dword [sy], 1
        add dword [y], 1
        jmp _bltrgba
        _endblt:
        ret 
    """ 
    return code

def _blt_rgba_to_prgba_code():
    bits = platform.architecture()[0]
    if bits == '64bit':
        return _blt_floatrgba_code64()
    else:
        return _blt_floatrgba_code32()

_asm = Tdasm()
_mc = _asm.assemble(_blt_rgba_to_prgba_code())
_runtime = Runtime()
_data_section = _runtime.load("blt_rgba_to_prgba", _mc)


def blt_rgba_to_prgba(src, dest):

    assert isinstance(src, ImageRGBA)
    assert isinstance(dest, ImagePRGBA)

    #TODO blt only part of image
    sa, spitch = src.address_info() 
    da, dpitch = dest.address_info()
    dx = dy = sx = sy = 0
    sw, sh = src.size()

    ds = _data_section
    ds["da"] = da
    ds["sa"] = sa
    ds["dx16"] = dx * 16 
    ds["sx4"] = sx * 4
    ds["sy"] = sy
    ds["spitch"] = spitch
    ds["dpitch"] = dpitch
    ds["y"] = dy
    ds["y2"] = dy + sh
    ds["sw"] = sw
    _runtime.run("blt_rgba_to_prgba")
    return True

