
irender.options(asm=True, spectral=False, pixel_size=1)
irender.set_camera(type="perspective", eye=(20, 20, 20), lookat=(0,0,0), distance=400)

irender.add_light(type="pointlight", name="light3", source=(1.0, 1.0, 1.0), position=(20,20,20))

irender.add_material(name="phong1", type="phong", diffuse=(0.1,0.1,0.1), specular=(0.2,0.2,0.2), n=2.2, samplings="default")
irender.add_material(name="phong2", type="phong", diffuse=(0.3,0.1,0.2), specular=(0.2,0.2,0.2), n=2.2, samplings="default")

irender.add_shape(type="mesh", name="cube1", filename="I:/Obj_files/fang_obj.obj", mtl="i:/Obj_files/fang_obj.mtl")

