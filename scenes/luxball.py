
irender.options(asm=True, spectral=False, pixel_size=0.1, spp=1, threads=4)
irender.set_camera(type="perspective", eye=(100, 150, 150), lookat=(50,0,0), distance=400)

irender.add_light(type="pointlight", name="light3", source=(1.0, 1.0, 1.0), position=(100,150,150))

irender.add_material(name="phong1", type="phong", diffuse=(0.1,0.1,0.1), specular=(0.2,0.2,0.2), n=2.2, samplings="default")
irender.add_material(name="phong2", type="phong", diffuse=(0.3,0.1,0.2), specular=(0.2,0.2,0.2), n=2.2, samplings="default")
irender.add_material(name="phong3", type="phong", diffuse=(0.3,0.3,0.3), specular=(0.4,0.4,0.4), n=2.2, samplings="default")
irender.add_material(name="phong4", type="phong", diffuse=(0.0,0.3,0.0), specular=(0.2,0.2,0.2), n=2.2, samplings="default")

irender.add_shape(type="mesh", name="cube1", filename="I:/Obj_files/luxball5.obj", mtl="I:/Obj_files/luxball5.mtl")

