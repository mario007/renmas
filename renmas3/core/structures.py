

RECTANGLE = """
    struct rectangle
    float point[4] 
    float normal[4]
    float edge_a[4]
    float edge_b[4]
    float edge_a_squared
    float edge_b_squared
    uint32 material
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
    uint32 material
    uint32 flags
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

FLAT_MESH = """
    struct flat_mesh
    uint32 vertex_buffer_ptr
    uint32 vertex_size
    uint32 triangle_buffer_ptr
    uint32 triangle_size
    uint32 mat_index
    float bbox_min[4]
    float bbox_max[4]
    float nbox_width[4]
    float n_1[4]
    float one_overn[4]
    int32 grid_size[4]
    uint32 grid_ptr
    uint32 array_ptr

    end struct
"""

SMOOTH_MESH = """
    struct smooth_mesh
    uint32 vertex_buffer_ptr
    uint32 vertex_size
    uint32 triangle_buffer_ptr
    uint32 triangle_size
    uint32 mat_index
    float bbox_min[4]
    float bbox_max[4]
    float nbox_width[4]
    float n_1[4]
    float one_overn[4]
    int32 grid_size[4]
    uint32 grid_ptr
    uint32 array_ptr

    end struct
"""

