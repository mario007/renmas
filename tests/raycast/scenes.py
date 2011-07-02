
import renmas
import renmas.interface as ren 

WIDTH = 300 
HEIGHT = 300 
NSAMPLES = 16 

def cornell_scene():
    s_props = {"type":"random", "pixel":1.0, "width": WIDTH, "height": HEIGHT, "nsamples": NSAMPLES}
    s =ren.create_sampler(s_props)

    c_props = {"type":"pinhole", "eye":(27.6, 27.4, -80), "lookat":(27.6, 27.4, 0.0), "distance":400}
    c = ren.create_camera(c_props)

    f_props = {"width": WIDTH, "height": HEIGHT, "nsamples": NSAMPLES}
    f = ren.create_film(f_props)

    #area light
    l_props = {"type":"area", "spectrum":(48, 46, 35), "shape":"rectangle", "p":(21.3, 54.87999, 22.7),
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

