
from tdasm import Tdasm

asm = Tdasm()
AVX = asm.avx_supported()
#AVX = False

SSSE3 = asm.cpu["ssse3"]
#SSSE3 = False
SSE3 = asm.cpu["sse3"]
SSE41 = asm.cpu["sse41"]
SSE2 = asm.cpu["sse2"]

