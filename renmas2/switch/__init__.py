
from tdasm import Tdasm

__asm = Tdasm()
AVX = __asm.avx_supported()
AVX = False

SSSE3 = __asm.cpu["ssse3"]
#SSSE3 = False
SSE3 = __asm.cpu["sse3"]
SSE41 = __asm.cpu["sse41"]
#SSE41 = False
SSE2 = __asm.cpu["sse2"]

