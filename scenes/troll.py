
irender.options(asm=True, spectral=False, pixel_size=0.2, spp=1, threads=4)
irender.set_camera(type="perspective", eye=(0, 20, 500), lookat=(0,60,0), distance=400)

irender.add_light(type="pointlight", name="light1", source=(1.5, 1.5, 1.5), position=(-500,400,500))
irender.add_light(type="pointlight", name="light2", source=(1.0, 1.0, 1.0), position=(60,250,1000))

irender.add_shape(type="mesh", name="cube1", filename="C:/Users/Mario/Desktop/troll.obj", mtl="C:/Users/Mario/Desktop/troll.mtl")

