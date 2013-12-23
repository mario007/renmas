
from tdasm import iset_supported

AVX = iset_supported('avx')
AVX = False

SSSE3 = iset_supported('ssse3')
#SSSE3 = False
SSE3 = iset_supported('sse3')
SSE41 = iset_supported('sse41')
#SSE41 = False
SSE2 = iset_supported('sse2')
