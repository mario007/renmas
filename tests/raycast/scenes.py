
import renmas
import renmas.interface as ren 

WIDTH = 420 
HEIGHT = 420 
NSAMPLES = 512 

def dragon():
    width = 800 
    height = 800 
    nsamples = 16 

    s_props = {"type":"random", "pixel":0.8, "width": width, "height": height, "nsamples": nsamples}
    s =ren.create_sampler(s_props)

    c_props = {"type":"pinhole", "eye":(10.0, 11.0, 10.0), "lookat":(0.0, 0.0, 0.0), "distance":400}
    c_props = {"type":"pinhole", "eye":(0.0, 0.0, 2.0), "lookat":(0.0, 0.12, 0.0), "distance":400}
    c = ren.create_camera(c_props)

    f_props = {"width": width, "height": height, "nsamples": nsamples}
    f = ren.create_film(f_props)

    #create lights
    #l_props = {"type":"point", "name": "light1", "position":(5,5.5,5.2), "spectrum":(4.99,4.99,4.99)}
    l_props = {"type":"area", "spectrum":(148, 148, 148), "shape":"rectangle", "p":(21.3, 24.87999, 22.7),
            "edge_a":(0.0, 0.0, 10.5), "edge_b":(13.0, 0.0, 0.0), "normal":(0.0, -1.0, 0.0)}
    l = ren.create_light(l_props)

    m_props = {"name": "m1", "sampling":"hemisphere_cos"}
    m = ren.create_material(m_props)
    m_props = {"type":"lambertian", "R":(0.342, 0.155, 0.115)} # left wall- red wall
    ren.add_brdf("m1", m_props)
    m_props = {"type":"phong", "R":(0.2, 0.2, 0.2), "e": 12.2, "k":0.3}
    ren.add_brdf("m1", m_props)

    m_props = {"name": "m2", "sampling":"hemisphere_cos"}
    m = ren.create_material(m_props)
    m_props = {"type":"lambertian", "R":(0.142, 0.315, 0.015)} # left wall- red wall
    ren.add_brdf("m2", m_props)
    m_props = {"type":"phong", "R":(0.2, 0.2, 0.2), "e": 12.2, "k":0.3}
    ren.add_brdf("m2", m_props)

    m_props = {"name": "m3", "sampling":"hemisphere_cos"}
    m = ren.create_material(m_props)
    m_props = {"type":"lambertian", "R":(0.142, 0.115, 0.315)} # left wall- red wall
    ren.add_brdf("m3", m_props)
    m_props = {"type":"phong", "R":(0.2, 0.2, 0.2), "e": 12.2, "k":0.3}
    ren.add_brdf("m3", m_props)

    #sh_props = {"type":"sphere", "position":(0,0,0), "radius":2, "material":"m1"}
    #s = ren.create_shape(sh_props)

    sh_props = {"type":"mesh", "resource":["Horse97K.ply"], "material":"m1", "scale": (2.5, 2.5, 2.5), "translate":(0.0, 0.0, 0.0)}
    #s = ren.create_shape(sh_props)

    sh_props = {"type":"mesh", "resource":["dragon_vrip_res4.ply"], "material":"m2" , "translate":(0.5,0.5,0), "scale":(4, 4, 4)}
    #sh_props = {"type":"mesh", "resource":["dragon_vrip_res3.ply"], "material":"m2"}
    #sh_props = {"type":"mesh", "resource":["dragon_vrip.ply"], "material":"m1"}
    sh_props = {"type":"mesh", "resource":["dragon_vrip.ply"], "material":"m2" , "translate":(0.2,-1.65,0), "scale":(12, 12, 12)}
    #sh_props = {"type":"mesh", "resource":["dragon_vrip_res2.ply"], "material":"m2" , "translate":(0.2,-1.35,0), "scale":(8, 8, 8)}
    s = ren.create_shape(sh_props)

    sh_props = {"type":"mesh", "resource":["dragon_vrip_res4.ply"], "material":"m3" , "translate":(-2.5,0.0,0), "scale":(4, 4, 4)}
    #s = ren.create_shape(sh_props)

    #floor
    sh_props = {"type":"rectangle", "p":(-8.0, -1.0, -4.0), "edge_a":(0.0, 0.0, 100.00), "edge_b":(100.00, 0.0, 0.0), "normal":(0.0, 1.0, 0.0) ,"material":"m1"}
    s = ren.create_shape(sh_props)


def cornell_scene():
    s_props = {"type":"random", "pixel":300/WIDTH, "width": WIDTH, "height": HEIGHT, "nsamples": NSAMPLES}
    s =ren.create_sampler(s_props)

    c_props = {"type":"pinhole", "eye":(27.6, 27.4, -80), "lookat":(27.6, 27.4, 0.0), "distance":400}
    c = ren.create_camera(c_props)

    f_props = {"width": WIDTH, "height": HEIGHT, "nsamples": NSAMPLES}
    f = ren.create_film(f_props)

    #area light
    #l_props = {"type":"area", "spectrum":(48, 46, 35), "shape":"rectangle", "p":(21.3, 54.87999, 22.7),
    l_props = {"type":"area", "spectrum":(48, 48, 48), "shape":"rectangle", "p":(21.3, 54.87999, 22.7),
            "edge_a":(0.0, 0.0, 10.5), "edge_b":(13.0, 0.0, 0.0), "normal":(0.0, -1.0, 0.0)}
    l = ren.create_light(l_props)

    m_props = {"name": "m1", "sampling":"hemisphere_cos"}
    m = ren.create_material(m_props)
    m_props = {"type":"lambertian", "R":(0.6, 0.6, 0.6)} # back wall - white wall
    ren.add_brdf("m1", m_props)

    m_props = {"name": "m2", "sampling":"hemisphere_cos"}
    m = ren.create_material(m_props)
    m_props = {"type":"lambertian", "R":(0.342, 0.015, 0.015)} # left wall- red wall
    ren.add_brdf("m2", m_props)

    m_props = {"name": "m3", "sampling": "hemisphere_cos"}
    m = ren.create_material(m_props)
    m_props = {"type":"lambertian", "R":(0.222, 0.354, 0.12)} # right wall- green wall
    ren.add_brdf("m3", m_props)
    m_props = {"type":"phong", "R":(0.22, 0.63, 0.53), "e": 12.2, "k":0.3}
    ren.add_brdf("m3", m_props)

    m_props = {"name": "m4", "sampling": "hemisphere_cos"}
    m = ren.create_material(m_props)
    m_props = {"type":"lambertian", "R":(0.99, 0.99, 0.0)} # right wall- green wall
    ren.add_brdf("m4", m_props)
    m_props = {"type":"phong", "R":(1.0, 1.0, 1.0), "e": 12.2, "k":0.3}
    ren.add_brdf("m4", m_props)

    m_props = {"name": "m5", "sampling": "hemisphere_cos"}
    m = ren.create_material(m_props)
    m_props = {"type":"lambertian", "R":(135/255, 206/255, 1.0)} # right wall- green wall
    ren.add_brdf("m5", m_props)
    m_props = {"type":"phong", "R":(1.0, 1.0, 1.0), "e": 12.2, "k":0.3}
    ren.add_brdf("m5", m_props)

    #back wall
    sh_props = {"type":"rectangle", "p":(0.0, 0.0, 55.92), "edge_a":(55.28, 0.0, 0.0), "edge_b":(0.0, 54.88, 0.0), "normal":(0.0, 0.0, -1.0) ,"material":"m1"}
    s = ren.create_shape(sh_props)

    #left wall
    sh_props = {"type":"rectangle", "p":(55.28, 0.0, 0.0), "edge_a":(0.0, 0.0, 55.92), "edge_b":(0.0, 54.88, 0.0), "normal":(-1.0, 0.0, 0.0) ,"material":"m2"}
    s = ren.create_shape(sh_props)

    #right wall
    sh_props = {"type":"rectangle", "p":(0.0, 0.0, 0.0), "edge_a":(0.0, 0.0, 55.92), "edge_b":(0.0, 54.88, 0.0), "normal":(1.0, 0.0, 0.0) ,"material":"m3"}
    s = ren.create_shape(sh_props)

    #floor
    sh_props = {"type":"rectangle", "p":(0.0, 0.0, 0.0), "edge_a":(0.0, 0.0, 55.92), "edge_b":(55.28, 0.0, 0.0), "normal":(0.0, 1.0, 0.0) ,"material":"m1"}
    s = ren.create_shape(sh_props)

    #ceiling
    sh_props = {"type":"rectangle", "p":(0.0, 54.88, 0.0), "edge_a":(0.0, 0.0, 55.92), "edge_b":(55.28, 0.0, 0.0), "normal":(0.0, -1.0, 0.0) ,"material":"m1"}
    s = ren.create_shape(sh_props)
    # short box
    #top
    sh_props = {"type":"rectangle", "p":(13.0, 16.5, 6.5), "edge_a":(-4.8, 0.0, 16.0), "edge_b":(16.0, 0.0, 4.9), "normal":(0.0, 1.0, 0.0) ,"material":"m1"}
    s = ren.create_shape(sh_props)
    #side 1
    sh_props = {"type":"rectangle", "p":(13.0, 0.0, 6.5), "edge_a":(-4.8, 0.0, 16.0), "edge_b":(0.0, 16.5, 0.0),
            "normal":(-0.95782628, 0.0, -0.2873478) ,"material":"m1"}
    s = ren.create_shape(sh_props)
    #side 2
    sh_props = {"type":"rectangle", "p":(8.2, 0.0, 22.5), "edge_a":(15.8, 0.0, 4.7), "edge_b":(0.0, 16.5, 0.0),
            "normal":(-0.2851209, 0.0, 0.95489155) ,"material":"m1"}
    s = ren.create_shape(sh_props)
    #side 3
    sh_props = {"type":"rectangle", "p":(24.2, 0.0, 27.4), "edge_a":(4.8, 0.0, -16.0), "edge_b":(0.0, 16.5, 0.0),
            "normal":(0.95782628, 0.0, 0.28734788) ,"material":"m1"}
    s = ren.create_shape(sh_props)
    #side 4
    sh_props = {"type":"rectangle", "p":(29, 0.0, 11.4), "edge_a":(-16.0, 0.0, -4.9), "edge_b":(0.0, 16.5, 0.0),
            "normal":(0.29282578, 0.0, -0.9561658) ,"material":"m1"}
    s = ren.create_shape(sh_props)

    # tall box
    #top
    sh_props = {"type":"rectangle", "p":(42.3, 33.0, 24.7), "edge_a":(-15.8, 0.0, 4.9), "edge_b":(4.9, 0.0, 15.9), "normal":(0.0, 1.0, 0.0) ,"material":"m1"}
    s = ren.create_shape(sh_props)
    #side 1
    sh_props = {"type":"rectangle", "p":(42.3, 0.0, 24.7), "edge_a":(-15.8, 0.0, 4.9), "edge_b":(0.0, 33.0, 0.0),
            "normal":(-0.296209, 0.0, -0.955123) ,"material":"m1"}
    s = ren.create_shape(sh_props)
    #side 2
    sh_props = {"type":"rectangle", "p":(26.5, 0.0, 29.6), "edge_a":(4.9, 0.0, 15.9), "edge_b":(0.0, 33.0, 0.0),
            "normal":(-0.9556489, 0.0, 0.294508) ,"material":"m1"}
    s = ren.create_shape(sh_props)
    #side 3
    sh_props = {"type":"rectangle", "p":(31.4, 0.0, 45.5), "edge_a":(15.8, 0.0, -4.9), "edge_b":(0.0, 33.0, 0.0),
            "normal":(0.296209, 0.0, 0.95512312) ,"material":"m1"}
    s = ren.create_shape(sh_props)
    #side 4
    sh_props = {"type":"rectangle", "p":(47.2, 0.0, 40.6), "edge_a":(-4.9, 0.0, -15.9), "edge_b":(0.0, 33.0, 0.0),
            "normal":(0.95564, 0.0, -0.2945) ,"material":"m1"}
    s = ren.create_shape(sh_props)

    """import random
    for x in range(500):
        sh_props = {"type":"sphere", "position":(random.random()*45.0 + 5.0,random.random()*25,random.random()*45+5.0), "radius":random.random(), "material":"m4"}
        s = ren.create_shape(sh_props)
    for x in range(500):
        sh_props = {"type":"sphere", "position":(random.random()*45.0 + 5.0,random.random()*25,random.random()*45+5.0), "radius":random.random(), "material":"m3"}
        s = ren.create_shape(sh_props)
    for x in range(500):
        sh_props = {"type":"sphere", "position":(random.random()*45.0 + 5.0,random.random()*25,random.random()*45+5.0), "radius":random.random(), "material":"m5"}
        s = ren.create_shape(sh_props)"""

