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
    float v0[4]
    float v1[4]
    float v2[4]
    float n0[4]
    float n1[4]
    float n2[4]
    float normal[4]
    float u
    float v
    uint32 mat_index
    uint32 flags
    end struct
"""

HITPOINT = """
    struct hitpoint
    float hit[4]
    float normal[4]
    float t
    uint32 mat_index
    float wi[4]
    float wo[4]
    float light_normal[4]
    float light_sample[4]
    uint32 visible 
    float ndotwi
    float pdf
    float light_pdf
    uint32 specular
    spectrum le_spectrum
    spectrum f_spectrum 
    spectrum l_spectrum 
    end struct
"""

MATERIAL = """
    struct material
    float spectrum[4]
    uint32 ptr_function
    end struct
"""

SAMPLE = """
    struct sample
    float xyxy[4] 
    uint32 ix, iy
    float weight 
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
        "material": MATERIAL,
        "plane": PLANE,
        "rectangle": RECTANGLE,
        "triangle": TRIANGLE,
        "sample": SAMPLE,
        'grid': GRID,
        "mesh3d": MESH3D
        }

class Structures:
    def __init__(self, renderer):
        self.tdasm = Tdasm()
        self.renderer = renderer

        self._line1 = "struct spectrum \n"
        self._line3 = "end struct \n"
    
    def get_struct(self, name):
        if name in structures:
            return structures[name]
        elif name == "spectrum":
            if self.renderer.spectral_rendering:
                line2 = "float values[" + str(self.renderer.nspectrum_samples) + "] \n"
            else:
                line2 = "float values[4] \n"
            return self._line1 + line2 + self._line3
        elif name == "hitpoint":
            if self.renderer.spectral_rendering:
                line2 = "float values[" + str(self.renderer.nspectrum_samples) + "] \n"
            else:
                line2 = "float values[4] \n"
            spec = self._line1 + line2 + self._line3
            return spec + HITPOINT
        return None

    def get_compiled_struct(self, name):
        if name in structures:
            asm_code = """ #DATA
            """
            asm_code += self.get_struct(name) 
            asm_code += """
            #CODE
            #END
            """
            mc = self.tdasm.assemble(asm_code)
            return mc.get_struct(name)
        return None

    def structs(self, names):
        code = ""
        for name in names:
            struct = self.get_struct(name)
            if struct is None:
               raise ValueError("Structure " + str(name) + " doesn't exist!")
            code += struct
        return code

