from math import sqrt

def tir(incident, normal, n1, n2):
    n = n1 / n2
    cosi = -normal.dot(incident)
    sint2 = n * n * (1.0 - cosi * cosi)
    if sint2 > 1.0: return True #TIR 
    return False

# xmm0 = incident 
# xmm1 = normal 
# xmm2 = n1
# xmm3 = n2
# result
# eax = 1 if TIR otherwise 0
def tir_asm(assembler):

    code = """
     #DATA
     float one[4] = 1.0, 1.0, 1.0, 0.0
     float minus_one[4] = -1.0, -1.0, -1.0, 0.0
     #CODE
     global tir:
     macro eq32 xmm4 = xmm2 / xmm3
     macro dot xmm5 = xmm1 * xmm0 {xmm6, xmm7}
     macro eq32 xmm5 = xmm5 * minus_one
     macro eq32 xmm5 = xmm5 * xmm5 
     macro eq32 xmm6 = xmm4 * xmm4
     macro eq32 xmm7 = one - xmm5
     macro eq32 xmm6 = xmm6 * xmm7
     macro if xmm6 > one goto _tir_ocured
     mov eax, 0
     ret

     _tir_ocured:
     mov eax, 1
     ret 
    """
    mc = assembler.assemble(code, True)
    return mc

def refract(incident, normal, n1, n2):
    n = n1 / n2
    cosi = -normal.dot(incident)
    sint2 = n * n * (1.0 - cosi * cosi)
    if sint2 > 1.0: return None #TIR 
    cost = sqrt(1.0 - sint2) 
    return incident * n + normal * (n * cosi - cost)

# xmm0 = incident 
# xmm1 = normal 
# xmm2 = n1
# xmm3 = n2
# result
# xmm0 = transmit vector and eax = 0
# if TIR ocured xmm0 = null vector and eax = 1
def refract_asm(assembler):

    code = """
     #DATA
     float one[4] = 1.0, 1.0, 1.0, 0.0
     float minus_one[4] = -1.0, -1.0, -1.0, 0.0
     #CODE
     global refract:
     macro eq32 xmm4 = xmm2 / xmm3
     macro dot xmm5 = xmm1 * xmm0 {xmm6, xmm7}
     macro eq32 xmm5 = xmm5 * minus_one
     macro eq32 xmm2 = xmm4 * xmm4
     macro eq32 xmm3 = xmm5 * xmm5
     macro eq32 xmm6 = one - xmm3
     macro eq32 xmm6 = xmm6 * xmm2 
     macro if xmm6 > one goto _tir_ocured
    
     macro eq32 xmm7 = one - xmm6
     macro call sqrtss xmm7, xmm7
     macro eq32 xmm6 = xmm4 * xmm5 - xmm7
     macro broadcast xmm6 = xmm6[0]
     macro eq128 xmm1 = xmm1 * xmm6
     macro broadcast xmm4 = xmm4[0]
     macro eq128 xmm0 = xmm0 * xmm4 + xmm1
     mov eax, 0
     ret

     _tir_ocured:
     mov eax, 1
     macro call zero xmm0
     ret 
    """
    mc = assembler.assemble(code, True)
    return mc

