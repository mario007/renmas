import time
from renmas3.loaders import load_meshes
from renmas3.win32 import show_image_in_window
from renmas3.loaders import load_image

start = time.clock()
#mesh_descs = load_meshes("Box.obj")
mesh_descs = load_meshes("CornellNeg.obj")
#mesh_descs = load_meshes("I:\\ray_tracing_scenes\\san-miguel\\san-miguel.obj")
#mesh_descs = load_meshes("I:\\ray_tracing_scenes\\dragon\\dragon.obj")
#mesh_descs = load_meshes("I:\\ray_tracing_scenes\\rungholt\\rungholt.obj")
#mesh_descs = load_meshes("I:\\ray_tracing_scenes\\powerplant\\powerplant.obj")
#mesh_descs = load_meshes("I:\\ray_tracing_scenes\\hairball\\hairball.obj")
#mesh_descs = load_meshes("cube.ply")
#mesh_descs = load_meshes("I:\\Ply_files\\lucy.ply")
#mesh_descs = load_meshes("I:\\Ply_files\\g3.ply")

end = time.clock()
print("Loading of meshes took ", end-start)
nvertices = 0
ntriangles = 0
if mesh_descs:
    for m in mesh_descs:
        print(m.name, m.vb.size(), m.tb.size(), type(m.vb))
        nvertices += m.vb.size()
        ntriangles += m.tb.size()

#vb = mesh_descs[0].vb
#for i in range(vb.size()):
#    print(vb.get(i))

print(nvertices, ntriangles, len(mesh_descs))
img = load_image("rle.tga")
if img is not None:
    show_image_in_window(img)

