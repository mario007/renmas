from random import random

irender.options(asm=True, spectral=False, pixel_size=1.0)
irender.set_camera(type="perspective", eye=(12, 12, 12), lookat=(0,0,0), distance=400)

irender.add_light(type="pointlight", name="light2", source=(1.0,1.0,1.0), position=(12,10,10))
irender.add_material(name="phong1", type="phong", diffuse=(0.3,0.4,0.2), specular=(0.3,0.3,0.3), n=2.2, samplings="default")


for i in range(30):
    irender.add_shape(type="sphere", name="Sphere00" + str(i), radius=random()*0.5, 
            position=(random()*5.0, random()*5.0, random()*5.0), material="phong1")

