
#1000, 800
irender.options(asm=True, spectral=False, pixel_size=0.38)
irender.set_camera(type="perspective", eye=(280, 110, 244), lookat=(80,100,0), distance=400)

irender.add_light(type="pointlight", name="light1", source=(4.0, 4.0, 4.0), position=(30,110,-80))
irender.add_light(type="pointlight", name="light2", source=(1.0, 1.0, 1.0), position=(100,280,200))
irender.add_light(type="environment", name="light5", source=(0.2,0.2,0.2))

irender.add_material(name="phong1", type="phong", diffuse=(0.1,0.1,0.1), specular=(0.2,0.2,0.2), n=2.2, samplings="default")
irender.add_material(name="phong2", type="phong", diffuse=(0.3,0.1,0.2), specular=(0.2,0.2,0.2), n=2.2, samplings="default")
irender.add_material(name="phong3", type="phong", diffuse=(0.1,0.1,0.1), specular=(0.2,0.2,0.2), n=2.2, samplings="default")
irender.add_material(name="phong4", type="phong", diffuse=(0.3,0.1,0.2), specular=(0.2,0.2,0.2), n=2.2, samplings="default")
irender.add_material(name="phong5", type="phong", diffuse=(0.1,0.1,0.1), specular=(0.2,0.2,0.2), n=2.2, samplings="default")
irender.add_material(name="phong6", type="phong", diffuse=(0.3,0.1,0.2), specular=(0.2,0.2,0.2), n=2.2, samplings="default")

comp1 = {"type":"perfect_specular", "specular":(1.0, 1.0, 1.0), "ior":1.05}
comp2 = {"type":"perfect_transmission", "specular":(0.9, 0.9, 1.0), "ior":1.05}
irender.add_material(name="dielectric1", components=[comp1, comp2])

#irender.add_shape(type="mesh", name="cube1", filename="I:/Obj_files/mini_obj.obj")
irender.add_shape(type="mesh", name="cube1", filename="G:/Obj_files/mini_with_walls.obj")


