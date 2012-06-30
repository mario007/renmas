
def reflect(incident, normal):
    return incident - normal * (normal.dot(incident) * 2.0)  

# xmm0 = incident 
# xmm1 = normal 
# result
# xmm0 = reflect vector
def reflect_asm(assembler):

    code = """
     #DATA
     float two[4] = 2.0, 2.0, 2.0, 0.0
     #CODE
     global reflect:
     macro dot xmm2 = xmm0 * xmm1 {xmm6, xmm7}
     macro eq32 xmm2 = xmm2 * two
     macro broadcast xmm2 = xmm2[0]
     macro eq128 xmm2 = xmm2 * xmm1 
     macro eq128 xmm0 = xmm0 - xmm2
     ret 
    """
    mc = assembler.assemble(code, True)
    return mc

