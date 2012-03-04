

irender.options(asm=True, spectral=True, pixel_size=1.0)

irender.add_light(type="pointlight", name="light2", source=(1.0,1.0,1.0), position=(6,10,10))
irender.add_material(name="phong1", type="phong", diffuse=(0.3,0.1,0.2), specular=(0.2,0.2,0.2), n=2.2, samplings="default")

irender.add_shape(type="sphere", name="Sphere00", radius=3.0, position=(0.0, 0.0, 0.0), material="phong1")

