
irender.options(asm=True, spectral=False, pixel_size=0.5, width=600, height=600, spp=160, threads=4)
irender.set_camera(type="perspective", eye=(10.0, 11.0, 10.0), lookat=(0.0,0.0,0.0), distance=400)


irender.add_light(type="pointlight", name="light3", source=(2.99, 2.99, 2.99), position=(5, 5.5, 5.2))

comp1 = {"type":"oren", "roughness":0.48, "diffuse":(0.2, 0.4, 0.7)}
comp2 = {"type":"ward", "alpha":0.1, "beta":1.0, "specular":(0.3, 0.3, 0.3)}
irender.add_material(name="ward1", components=[comp1,comp2], samplings="lambertian")

irender.add_shape(type="sphere", name="Sphere00", radius=3.0, position=(0.0, 0.0, 0.0), material="ward1")
irender.add_shape(type="rectangle", name="Rectangle1", P=(-8.0,-1.0,-4.0), Edge_a=(0.0,0.0,100.00), Edge_b=(100,0,0), Normal=(0,1,0))


