

irender.options(asm=True)
renderer.spectral_rendering = True
irender.add_shape(type="sphere", name="Sphere00", radius=3.0, position=(0.0, 0.0, 0.0))

irender.add_light(type="pointlight", name="light1", source=(4.0,4.0,4.0), position=(10,10,10))

