
irender.options(asm=False, spectral=False, pixel_size=2.0, width=400, height=400, spp=1, threads=1)
irender.set_camera(type="perspective", eye=(2.0, 50.0, -3.0), lookat=(2.0,0.0,-3.0), distance=1800)


irender.add_light(type="pointlight", name="light3", source=(4.5,4.5,4.5), position=(-10,20,10))
irender.add_light(type="pointlight", name="light4", source=(4.5,4.5,4.5), position=(40,50,0))

comp1 = {"type":"lambertian", "diffuse":(0.3, 0.0, 0.0)}
comp2 = {"type":"phong", "specular":(0.2, 0.2, 0.2), "n":2000, "sampling":"phong"}
irender.add_material(name="phong1", components=[comp1, comp2])

comp1 = {"type":"perfect_specular", "specular":(0.1, 0.1, 0.1), "ior":1.0}
comp2 = {"type":"perfect_transmission", "specular":(0.9, 0.9, 0.9), "ior":1.0}
comp3 = {"type":"phong", "specular":(0.2, 0.2, 0.2), "n":2000, "sampling":"phong"}
irender.add_material(name="dielectric1", components=[comp1, comp2, comp3])

irender.add_shape(type="sphere", name="RedSphere", radius=3.0, position=(4.0, 4.0, -6.0), material="phong1")
irender.add_shape(type="sphere", name="Sphere01", radius=3.0, position=(0.0, 4.5, 0.0), material="dielectric1")
irender.add_shape(type="rectangle", name="Rectangle1", P=(-20,-0.001,-100), Edge_a=(0.0,0.0,120.00), Edge_b=(40,0,0), Normal=(0,1,0))


