
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

HITPOINT = """
    struct hitpoint
    float hit[4]
    float normal[4]
    float t
    uint32 mat_index
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

structures = {
        "ray" : RAY, 
        "sphere": SPHERE,
        "hitpoint": HITPOINT,
        "material": MATERIAL,
        "pointlight":POINT_LIGHT,
        "plane": PLANE
        }

class AsmStructures:
    def __init__(self):
        pass
    
    def get_struct(self, name):
        if name in structures:
            return structures[name]
        return None

