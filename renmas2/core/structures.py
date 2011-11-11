from tdasm import Tdasm

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
RECTANGLE = """
    struct rectangle
    float point[4] 
    float normal[4]
    float edge_a[4]
    float edge_b[4]
    float edge_a_squared
    float edge_b_squared
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
    float brdf[4]
    float light_normal[4]
    float light_sample[4]
    float le[4]
    float t
    uint32 mat_index
    uint32 visible 
    float ndotwi
    float pdf
    float light_pdf
    uint32 specular
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
    ray cam_ray
    end struct
"""
GRID = """
    struct grid
    float bbox_min[4] 
    float bbox_max[4]
    float n_1[4]
    float nbox_width[4]
    float one_overn[4]
    int32 n[4]
    uint32 grid_ptr
    uint32 arr_ptr 
    end struct
"""

MESH3D = """
    struct mesh3d
    uint32 ptr_isect
    end struct
"""

structures = {
        "ray" : RAY, 
        "sphere": SPHERE,
        "hitpoint": HITPOINT,
        "material": MATERIAL,
        "pointlight":POINT_LIGHT,
        "plane": PLANE,
        "rectangle": RECTANGLE,
        "triangle": TRIANGLE,
        "sample": SAMPLE,
        'grid': GRID,
        "mesh3d": MESH3D
        }

class Structures:
    def __init__(self):
        self.tdasm = Tdasm()
    
    def get_struct(self, name):
        if name in structures:
            return structures[name]
        return None

    def get_compiled_struct(self, name):
        if name in structures:
            asm_code = """ #DATA
            """
            if name == "sample":
                asm_code += structures['ray']
            asm_code += structures[name]
            asm_code += """
            #CODE
            #END
            """
            mc = self.tdasm.assemble(asm_code)
            return mc.get_struct(name)
        return None

