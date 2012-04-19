
irender.options(asm=True, spectral=False, pixel_size=0.5, width=600, height=600, spp=1)

irender.add_light(type="pointlight", name="light2", source=(1.0,1.0,1.0), position=(-6,10,10))
irender.add_material(name="phong1", type="phong", diffuse=(0.3,1.8,0.2), specular=(0.4,0.4,0.4), n=2.2, samplings="lambertian")
irender.add_material(name="reflective1", type="phong", diffuse=(0.6,0.4,0.2), specular=(0.4, 0.4, 0.4), n=2.2,
        samplings="lambertian, perfect_specular")

comp1 = {"type":"oren", "roughness":0.48, "diffuse":(0.2, 0.4, 0.7)}
comp2 = {"type":"phong", "n":2.48, "specular":(0.3, 0.3, 0.3), "sampling":"phong"}
irender.add_material(name="rough1", components=[comp1,comp2], samplings="lambertian")

irender.add_shape(type="sphere", name="Sphere00", radius=2.0, position=(0.0, 0.0, 0.0), material="rough1")
irender.add_shape(type="sphere", name="Sphere01", radius=3.0, position=(5.0, 3.0, 1.0), material="reflective1")

