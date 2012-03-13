
irender.options(asm=True, spectral=False, pixel_size=0.5)
irender.set_camera(type="perspective", eye=(1, 1, 1), lookat=(0,0,0), distance=400)

irender.add_light(type="pointlight", name="light3", source=[(400,0.0), (500,1.6), (600,3.12), (700,3.68)], position=(100,100,100))

irender.add_material(name="phong1", type="phong", diffuse=(0.1,0.1,0.1), specular=(0.2,0.2,0.2), n=2.2, samplings="default")
irender.add_material(name="phong2", type="phong", diffuse=(0.3,0.1,0.2), specular=(0.2,0.2,0.2), n=2.2, samplings="default")

irender.add_shape(type="mesh", name="cube1", filename="I:/Ply_files/Horse97K.ply", material="phong1")

