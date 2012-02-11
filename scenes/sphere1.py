

irender.options(asm=True, spectral=False, pixel_size=1.0)
irender.add_shape(type="sphere", name="Sphere00", radius=3.0, position=(0.0, 0.0, 0.0))
irender.add_shape(type="sphere", name="Sphere01", radius=2.0, position=(4.0, 1.0, 3.0))
irender.add_shape(type="triangle", name="Triangle01", P0=(0,0,0), P1=(3.2,0,0), P2=(1.5,2,0))

irender.add_light(type="pointlight", name="light1", source=(2.0,2.0,2.0), position=(9,10,10))
irender.add_light(type="pointlight", name="light2", source=(1.0,1.0,1.0), position=(6,10,10))

