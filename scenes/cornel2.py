
irender.options(asm=True, spectral=False, pixel_size=0.5, width=600, height=600, spp=1, threads=1)
irender.set_camera(type="perspective", eye=(27.6, 27.4, -80.0), lookat=(27.6,27.4,0.0), distance=400)

#origina data for light
#irender.add_light(type="pointlight", name="light3", source="F1", position=(26,50.8,22))
irender.add_light(type="pointlight", name="light3", source=[(400,0.0), (500,8.0), (600,15.6), (700,18.4)], position=(26,50.8,22))

#irender.add_light(type="pointlight", name="light3", source=(1.0,1.0,1.0), position=(0.3,0.5,0.3))
#irender.add_light(type="pointlight", name="light3", source=[(400,0.0), (500,2.0), (600,3.9), (700,4.6)], position=(26,50.8,22))
#irender.add_light(type="pointlight", name="light3", source=[(400,0.0), (500,1.6), (600,3.12), (700,3.68)], position=(26,50.8,22))
#irender.add_light(type="pointlight", name="light4", source=[(400,0.0), (500,6.4), (600,12.48), (700,14.72)], position=(26,50.8,22))
#irender.add_light(type="pointlight", name="light4", source=[(400,0.0), (500,6.4), (600,12.48), (700,14.72)], position=(36,5.8,12))
#irender.add_light(type="pointlight", name="light3", source=[(400,0.0), (500,8.0), (600,15.6), (700,18.4)], position=(26,50.8,22))

white_source=[ (400, 0.343), (404, 0.445), (408, 0.551), (412, 0.624), (416, 0.665), (420, 0.687), (424, 0.708),
        (428, 0.723), (432, 0.715), (436, 0.710), (440, 0.745), (444, 0.758), (448, 0.739), (452, 0.767), (456, 0.777),
        (460, 0.765), (464, 0.751), (468, 0.745), (472, 0.748), (476, 0.729), (480, 0.745), (484, 0.757), (488, 0.753),
        (492, 0.750), (496, 0.746), (500, 0.747), (504, 0.735), (508, 0.732), (512, 0.739), (516, 0.734), (520, 0.725),
        (524, 0.721), (528, 0.733), (532, 0.725), (536, 0.732), (540, 0.743), (544, 0.744), (548, 0.748), (552, 0.728),
        (556, 0.716), (560, 0.733), (564, 0.726), (568, 0.713), (572, 0.740), (576, 0.754), (580, 0.764), (584, 0.752),
        (588, 0.736), (592, 0.734), (596, 0.741), (600, 0.740), (604, 0.732), (608, 0.745), (612, 0.755), (616, 0.751),
        (620, 0.744), (624, 0.731), (628, 0.733), (632, 0.744), (636, 0.731), (640, 0.712), (644, 0.708), (648, 0.729),
        (652, 0.730), (656, 0.727), (660, 0.707), (664, 0.703), (668, 0.729), (672, 0.750), (676, 0.760), (680, 0.751),
        (684, 0.739), (688, 0.724), (692, 0.730), (696, 0.740), (700, 0.737) ]
irender.add_material(name="white", type="lambertian", source=white_source,samplings="default")

comp1 = {"type":"perfect_specular", "specular":(0.9, 0.9, 0.9), "ior":1.6}
comp2 = {"type":"ward", "alpha":0.10, "beta":0.6, "specular":(0.8, 0.8, 0.8)}
comp3 = {"type":"lambertian", "diffuse":(0.2, 0.2, 0.2)}
irender.add_material(name="reflective_white", components=[comp1, comp2, comp3])
#irender.add_material(name="reflective_white", type="lambertian", source=(0.3,0.3,0.3),samplings="perfect_specular")


green_source=[ (400, 0.092), (404, 0.096), (408, 0.098), (412, 0.097), (416, 0.098), (420, 0.095), (424, 0.095),
        (428, 0.097), (432, 0.095), (436, 0.094), (440, 0.097), (444, 0.098), (448, 0.096), (452, 0.101), (456, 0.103),
        (460, 0.104), (464, 0.107), (468, 0.109), (472, 0.112), (476, 0.115), (480, 0.125), (484, 0.140), (488, 0.160),
        (492, 0.187), (496, 0.229), (500, 0.285), (504, 0.343), (508, 0.390), (512, 0.435), (516, 0.464), (520, 0.472),
        (524, 0.476), (528, 0.481), (532, 0.462), (536, 0.447), (540, 0.441), (544, 0.426), (548, 0.406), (552, 0.373),
        (556, 0.347), (560, 0.337), (564, 0.314), (568, 0.285), (572, 0.277), (576, 0.266), (580, 0.250), (584, 0.230),
        (588, 0.207), (592, 0.186), (596, 0.171), (600, 0.160), (604, 0.148), (608, 0.141), (612, 0.136), (616, 0.130),
        (620, 0.126), (624, 0.123), (628, 0.121), (632, 0.122), (636, 0.119), (640, 0.114), (644, 0.115), (648, 0.117),
        (652, 0.117), (656, 0.118), (660, 0.120), (664, 0.122), (668, 0.128), (672, 0.132), (676, 0.139), (680, 0.144),
        (684, 0.146), (688, 0.150), (692, 0.152), (696, 0.157), (700, 0.159) ]
irender.add_material(name="green", type="lambertian", source=green_source,samplings="default")

red_source=[ (400, 0.040), (404, 0.046), (408, 0.048), (412, 0.053), (416, 0.049), (420, 0.050), (424, 0.053),
        (428, 0.055), (432, 0.057), (436, 0.056), (440, 0.059), (444, 0.057), (448, 0.061), (452, 0.61), (456, 0.60),
        (460, 0.062), (464, 0.062), (468, 0.062), (472, 0.061), (476, 0.062), (480, 0.060), (484, 0.059), (488, 0.057),
        (492, 0.058), (496, 0.058), (500, 0.058), (504, 0.056), (508, 0.055), (512, 0.056), (516, 0.059), (520, 0.057),
        (524, 0.055), (528, 0.059), (532, 0.059), (536, 0.058), (540, 0.059), (544, 0.061), (548, 0.061), (552, 0.063),
        (556, 0.063), (560, 0.067), (564, 0.068), (568, 0.072), (572, 0.080), (576, 0.090), (580, 0.099), (584, 0.124),
        (588, 0.154), (592, 0.192), (596, 0.255), (600, 0.287), (604, 0.349), (608, 0.402), (612, 0.443), (616, 0.487),
        (620, 0.513), (624, 0.558), (628, 0.584), (632, 0.620), (636, 0.606), (640, 0.609), (644, 0.651), (648, 0.612),
        (652, 0.610), (656, 0.650), (660, 0.638), (664, 0.627), (668, 0.620), (672, 0.630), (676, 0.628), (680, 0.642),
        (684, 0.639), (688, 0.657), (692, 0.639), (696, 0.635), (700, 0.642) ]
irender.add_material(name="red", type="lambertian", source=red_source,samplings="default")

#create triangles for cornell
## BACK WALL
irender.add_shape(type="rectangle", name="Back_wall", material="white", P=(0,0,55.92), Edge_a=(55.28,0,0), Edge_b=(0,54.88,0), Normal=(0,0,-1))

## LEFT WALL
irender.add_shape(type="rectangle", name="Left_wall", material="red", P=(55.28,0,0), Edge_a=(0,0,55.92), Edge_b=(0,54.88,0), Normal=(-1,0,0))

## RIGHT WALL
irender.add_shape(type="rectangle", name="Right_wall", material="green", P=(0,0,0), Edge_a=(0,0,55.92), Edge_b=(0,54.88,0), Normal=(1,0,0))

## FLOOR
irender.add_shape(type="rectangle", name="Floor", material="white", P=(0,0,0), Edge_a=(0,0,55.92), Edge_b=(55.28,0,0), Normal=(0,1,0))

## CEILING
irender.add_shape(type="rectangle", name="Ceiling", material="white", P=(0,54.88,0), Edge_a=(0,0,55.92), Edge_b=(55.28,0,0), Normal=(0,-1,0))

# short box
#top
irender.add_shape(type="rectangle", name="short_top", material="red", P=(13,16.5,6.5), Edge_a=(-4.8,0,16), Edge_b=(16,0,4.9), Normal=(0,1,0))

irender.add_shape(type="rectangle", name="short_side1", material="white", P=(13,0,6.5), Edge_a=(-4.8,0,16), Edge_b=(0,16.5,0), Normal=(-0.95782628,0,-0.2873478))

irender.add_shape(type="rectangle", name="short_side2", material="white", P=(8.2,0,22.5), Edge_a=(15.8,0,4.7), Edge_b=(0,16.5,0), Normal=(-0.2851209,0,0.95489155))

irender.add_shape(type="rectangle", name="short_side3", material="white", P=(24.2,0,27.4), Edge_a=(4.8,0,-16), Edge_b=(0,16.5,0), Normal=(0.95782628,0,0.28734788))

irender.add_shape(type="rectangle", name="short_side4", material="white", P=(29,0,11.4), Edge_a=(-16,0,-4.9), Edge_b=(0,16.5,0), Normal=(0.29282578,0,-0.9561658))

# tall box
irender.add_shape(type="rectangle", name="tall_top", material="white", P=(42.3,33,24.7), Edge_a=(-15.8,0,4.9), Edge_b=(4.9,0,15.9), Normal=(0,1,0))

irender.add_shape(type="rectangle", name="tall_side1", material="reflective_white", P=(42.3,0,24.7), Edge_a=(-15.8,0,4.9), Edge_b=(0,33,0), Normal=(-0.296209,0,-0.955123))

irender.add_shape(type="rectangle", name="tall_side2", material="white", P=(26.5,0,29.6), Edge_a=(4.9,0,15.9), Edge_b=(0,33,0), Normal=(-0.9556489,0,0.294508))

irender.add_shape(type="rectangle", name="tall_side3", material="white", P=(31.4,0,45.5), Edge_a=(15.8,0,-4.9), Edge_b=(0,33,0), Normal=(0.296209,0,0.95512312))

irender.add_shape(type="rectangle", name="tall_side4", material="white", P=(47.2,0,40.6), Edge_a=(-4.9,0,-15.9), Edge_b=(0,33,0), Normal=(0.95564,0,-0.2945))

# Sphere
comp1 = {"type":"oren", "roughness":0.48, "diffuse":(0.2, 0.4, 0.7)}
comp2 = {"type":"phong", "n":2.48, "specular":(0.3, 0.3, 0.3), "sampling":"phong"}
irender.add_material(name="rough1", components=[comp1,comp2], samplings="lambertian")

comp1 = {"type":"oren", "roughness":1.0, "diffuse":(0.2, 0.4, 0.7)}
comp2 = {"type":"ward", "alpha":0.10, "beta":0.6, "specular":(0.8, 0.8, 0.8)}
irender.add_material(name="ward1", components=[comp1,comp2], samplings="lambertian")

#irender.add_shape(type="sphere", name="Sphere00", radius=9.0, position=(18.0, 35.0, 23.0), material="ward1")

#comp1 = {"type":"emission", "source":(2.2, 2.2, 2.2)}
#comp2 = {"type":"lambertian", "diffuse":(0.78, 0.78, 0.78)}
#irender.add_material(name="emission1", components=[comp1,comp2], samplings="lambertian")

#irender.add_shape(type="rectangle", name="top_light", material="emission1", P=(0,54.80, 0), Edge_a=(0, 0, 55.92), Edge_b=(55.28, 0,0), Normal=(0,-1,0))

