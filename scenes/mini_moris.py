
#1000, 800
irender.options(asm=True, spectral=False, pixel_size=0.38, width=900, height=900)
irender.set_camera(type="perspective", eye=(280, 110, 244), lookat=(80,70,0), distance=400)

irender.add_light(type="pointlight", name="light3", source=(1.0, 1.0, 1.0), position=(100,280,200))
#irender.add_light(type="environment", name="light5", source=(0.5,0.5,0.5))

irender.add_material(name="phong1", type="phong", diffuse=(0.1,0.1,0.1), specular=(0.2,0.2,0.2), n=2.2, samplings="default")
irender.add_material(name="phong2", type="phong", diffuse=(0.3,0.1,0.2), specular=(0.2,0.2,0.2), n=2.2, samplings="default")

irender.add_shape(type="mesh", name="cube1", filename="I:/Obj_files/mini_obj.obj")
#irender.add_shape(type="mesh", name="cube1", filename="G:/Obj_files/mini_with_walls.obj")

