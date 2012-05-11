
irender.options(asm=False, spectral=False, pixel_size=1.0, width=200, height=200, spp=1)
irender.set_camera(type="perspective", eye=(10, 0, 10), lookat=(0,20.1,0), distance=400)
#irender.set_camera(type="perspective", eye=(10, 10, 10), lookat=(0,0,0), distance=400)

irender.add_light(type="sunsky", name="sun1", latitude=20.0, longitude=0.0, sm=0, jd=40,
        time_of_day=15.00, turbidity=1.0)


comp1 = {"type":"oren", "roughness":0.48, "diffuse":(0.2, 0.4, 0.7)}
comp2 = {"type":"ward", "alpha":0.1, "beta":1.0, "specular":(0.3, 0.3, 0.3)}
irender.add_material(name="ward1", components=[comp1,comp2], samplings="lambertian")

#irender.add_shape(type="sphere", name="Sphere01", material="ward1", radius=1.5, position=(0.0, 0.0, 0.0))
#irender.add_shape(type="rectangle", name="Rectangle1", P=(-160.0,-1.0,-160.0), Edge_a=(0.0,0.0,200.00), Edge_b=(200,0,0), Normal=(0,1,0))

