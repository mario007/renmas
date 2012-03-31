
irender.options(asm=True, spectral=False, pixel_size=1.25)
#irender.set_camera(type="perspective", eye=(-250, 400, -100), lookat=(0,0,0), distance=400)
irender.set_camera(type="perspective", eye=(9000, 1600, -3000), lookat=(0,0,0), distance=400)

#irender.add_light(type="pointlight", name="light3", source=(1.0, 1.0, 1.0), position=(-250,400,-100))
irender.add_light(type="pointlight", name="light3", source=(1.0, 1.0, 1.0), position=(8500,1600,-2500))

irender.add_material(name="phong1", type="phong", diffuse=(0.1,0.1,0.1), specular=(0.2,0.2,0.2), n=2.2, samplings="default")
irender.add_material(name="phong2", type="phong", diffuse=(0.3,0.1,0.2), specular=(0.2,0.2,0.2), n=2.2, samplings="default")

#irender.add_shape(type="mesh", name="cube1", filename="I:/Obj_files/luxball.obj", material="phong1")
#irender.add_shape(type="mesh", name="cube1", filename="I:/Obj_files/auto_high.obj", mtl="I:/Obj_files/auto_high.mtl")
#irender.add_shape(type="mesh", name="cube1", filename="I:/Obj_files/test.obj", material="phong1")
irender.add_shape(type="mesh", name="cube1", filename="I:/Obj_files/primaca.obj", mtl="i:/Obj_files/primaca.mtl")
#irender.add_shape(type="mesh", name="cube1", filename="I:/Obj_files/AFHBC.obj", mtl="i:/Obj_files/AFHBC.mtl")

