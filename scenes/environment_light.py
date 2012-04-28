
irender.options(asm=False, spectral=False, pixel_size=1.0, width=200, height=200, spp=1)

irender.add_light(type="pointlight", name="light2", source=(1.0,1.0,1.0), position=(6,10,10))

irender.add_light(type="environment", name="light3", source=(0.3,0.3,0.3))

comp1 = {"type":"perfect_specular", "specular":(0.1, 0.1, 0.1), "ior":1.1}
comp2 = {"type":"perfect_transmission", "specular":(0.9, 0.9, 0.9), "ior":1.1}
#comp3 = {"type":"phong", "specular":(0.5, 0.5, 0.5), "n":2000, "sampling":"phong"}
comp3 = {"type":"phong", "specular":(0.5, 0.5, 0.5), "n":2000}
comp4 = {"type": "lambertian", "diffuse":(0.3,0.3,0.3)}
irender.add_material(name="phong1", components=[comp1, comp2])

irender.add_material(name="phong1", type="lambertian", source=(0.3,0.4,0.2), samplings="default")

irender.add_shape(type="sphere", name="Sphere00", radius=2.0, position=(0.0, 0.0, 0.0), material="phong1")
irender.add_shape(type="sphere", name="Sphere01", radius=2.5, position=(2.0, 0.0, -6.0))


