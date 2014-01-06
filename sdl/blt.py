
import platform
from tdasm import Tdasm, Runtime

def _blt_rect_code64():
    code  = """
        #DATA
        uint64 sa, da
        uint32 dx4, sx4, sy, sw
        uint32 y, y2, spitch, dpitch
        int32 inc_y = 1

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
        mov ebx, dword [sx4]
        add rsi, rbx
        mov ecx, dword [sw]

        ;rep movs dword [edi], dword [esi]
        _loop:
        mov eax, dword [rsi]
        mov dword [rdi], eax
        add rsi, 4
        add rdi, 4
        sub ecx, 1
        jnz _loop
        
        mov eax, dword [inc_y]
        add dword [sy], eax 
        add dword [y], 1
        jmp _bltrgba
        _endblt:
        ret 

    """
    return code

def _blt_rect_code32():
    code = """
        #DATA
        uint32 sa, da, dx4, sx4, sy, sw
        uint32 y, y2, spitch, dpitch
        int32 inc_y = 1

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
        
        mov eax, dword [inc_y]
        add dword [sy], eax 
        add dword [y], 1
        jmp _bltrgba
        _endblt:
        ret 
    """
    return code

def _blt_rect_code():
    bits = platform.architecture()[0]
    if bits == '64bit':
        return _blt_rect_code64()
    else:
        return _blt_rect_code32()

_mc = Tdasm().assemble(_blt_rect_code())
_runtime = Runtime()
_data_section = _runtime.load("bltrgba", _mc)

def blt_image(src, dest, sx=0, sy=0, sw=-1, sh=-1, dx=0, dy=0, fliped=False):
    """
        Transfer block of image from source to destination.

        @param src - source image 
        @param dest - destination image
        @param sx - x position in source image
        @param sy - y position in source image
        @param sw - width of source image
        @param sh - height of source image
        @param dx - x position in destination image
        @param dy - y position in destination image
        @param fliped - vertical flip of the image
        @return False if not even one byte is transferd, otherwise True
    """
    
    src_w, src_h = src.size()
    if sw == -1: sw = src_w
    if sh == -1: sh = src_h

    if sx < 0 or sy < 0: return False
    if sw <=0 or sh <=0: return False
    if dx < 0 or dy < 0: return False
    if sw > src_w - sx: sw = src_w - sx
    if sh > src_h - sy: sh = src_h - sy

    width, height = dest.size()
    dw = width - dx
    dh = height - dy
    if dw <=0 or dh <=0: return False
    if sw > dw: sw = dw 
    if sh > dh: sh = dh

    da, dpitch = dest.address_info()
    sa, spitch = src.address_info()

    return blt_rect(sa, sx, sy, sw, sh, spitch, da, dx, dy, dpitch, fliped)


def blt_rect(sa, sx, sy, sw, sh, spitch, da, dx, dy, dpitch, fliped=False):
    """
        Transfer block of memory from source to destination.
        Caution. Bounds are not checked.

        @param sa - source address
        @param sx - x position in source
        @param sy - y position in source
        @param sw - width of source rectangle
        @param sh - height of source rectangle
        @param spitch - number of bytes in row of source
        @param da - destination address
        @param dx - x position in destination
        @param dy - y position in destination
        @param dpitch - number of bytes in row of destination
        @param fliped - vertical flip of the rectangle
        @return False if not even one byte is transferd, otherwise True
    """

    if sx < 0 or sy < 0 or sw <= 0 or sh <= 0 or dx < 0 or dy < 0:
        return False

    ds = _data_section
    ds["da"] = da
    ds["sa"] = sa
    ds["dx4"] = dx * 4
    ds["sx4"] = sx * 4
    if fliped:
        ds["sy"] = sy + sh - 1
        ds["inc_y"] = -1
    else:
        ds["sy"] = sy
        ds["inc_y"] = 1
    ds["spitch"] = spitch
    ds["dpitch"] = dpitch
    ds["y"] = dy
    ds["y2"] = dy + sh
    ds["sw"] = sw

    _runtime.run("bltrgba")
    return True

