
RAY = """
    struct ray
    float dir[4]
    float origin[4]
    end struct
"""

SPHERE = """
    struct sphere
    float origin[4]
    float radius
    uint32 mat_index
    end struct
"""
PLANE = """
    struct plane
    float point[4] 
    float normal[4]
    uint32 mat_index
    end struct
"""

TRIANGLE = """
    struct triangle
    float p0[4]
    float p1[4]
    float p2[4]
    float normal[4]
    uint32 mat_index
    end struct
"""

HITPOINT = """
    struct hitpoint
    float hit[4]
    float normal[4]
    float wi[4]
    float wo[4]
    float spectrum[4]
    float t
    uint32 mat_index
    uint32 visible 
    float ndotwi
    end struct
"""

MATERIAL = """
    struct material
    float spectrum[4]
    uint32 ptr_function
    end struct
"""

POINT_LIGHT = """
    struct pointlight
    float spectrum[4]
    float position[4]
    end struct
"""

SAMPLE = """
    struct sample
    float xyxy[4] 
    uint32 ix, iy
    float weight 
    end struct
"""

structures = {
        "ray" : RAY, 
        "sphere": SPHERE,
        "hitpoint": HITPOINT,
        "material": MATERIAL,
        "pointlight":POINT_LIGHT,
        "plane": PLANE,
        "triangle": TRIANGLE,
        "sample": SAMPLE
        }

class AsmStructures:
    def __init__(self):
        pass
    
    def get_struct(self, name):
        if name in structures:
            return structures[name]
        return None

