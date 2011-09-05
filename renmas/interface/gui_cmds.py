
from .create import prepare_for_rendering, create_tiles, get_tile, get_integrator 
from .create import is_rendering_finished
from .create import get_film
from . import create 


import renmas
renderer = renmas.renderer # renderer
ren = renmas.ren #high level interface
log = renmas.log

#prepare_scene
#render
#is_finished
#ptr_image
#width_image
#height_image
#pitch image


# "eye" or "lookat" or "distance" - property type
# "X" or "Y" or "Z" or "d"- property name
#get_camera_prop()
#set_camera_prop()
#get_camera_type() - "perspective", "orthographic", ...
#create_perspective_camera, create_orthographic_camera 

#create_point_light
#create_area_light - PyRun_SimpleString
#get_num_lights
#get_names_of_lights - "light1,light2,..." - comma separated names
#get_type_light , params index or name of light
# "position", "spectrum",...
#get_light_prop(light_name, property_type, property_name)
#set_light_prop(light_name, property_type, proptety_name)


def prepare_scene():
    return renderer.prepare()

def render(): #render small part of picture
    res = renderer.render()
    film = renderer._film
    film.blt_image_to_buffer()

    return res

#FORMAT is float RGBA - 4byte per color channel- alpha channel is 1.0 
def ptr_image():
    film = renderer._film
    if film is None: return -1 
    #addr, pitch = film.image.get_addr()
    addr, pitch = film.frame_buffer.get_addr()
    return addr 
    
def width_image():
    film = renderer._film
    if film is None: return -1 
    #width, height = film.image.get_size()
    width, height = film.frame_buffer.get_size()
    return width

def height_image():
    film = renderer._film
    if film is None: return -1 
    #width, height = film.image.get_size()
    width, height = film.frame_buffer.get_size()
    return height

def pitch_image():
    film = renderer._film
    if film is None: return -1 
    #addr, pitch = film.image.get_addr()
    addr, pitch = film.frame_buffer.get_addr()
    return pitch

#main protocol methods - almost everthing must go through this two methos
def get_property(category, name):
    if category == "camera":
        return get_camera_props(name)
    elif category == "log":
        return log.handlers[0].get_logs()
    elif category == "global_settings":
        return get_global_settings(name)
    return ""

def set_property(category, name, value):
    if category == "camera":
        return set_camera_props(name, value)
    elif category == "global_settings":
        return set_global_settings(name, value)

    return 1


def get_camera_props(prop):
    text = ""
    if prop == "eye":
        eye = renderer.get_camera().eye
        text = str(eye.x) + "," + str(eye.y) + "," + str(eye.z) 
    elif prop == "lookat":
        lookat = renderer.get_camera().lookat
        text = str(lookat.x) + "," + str(lookat.y) + "," + str(lookat.z) 
    elif prop == "distance":
        distance = renderer.get_camera().distance
        text = str(distance)
    return text

def set_camera_props(prop, value):
    if prop == "eye":
        camera = renderer.get_camera()
        x, y, z = value.split(',')
        camera.set_eye(float(x), float(y), float(z))

    return 1

def get_global_settings(prop):
    text = ""
    if prop == "resolution": 
        width, height = renderer.get_resolution()
        text = str(width) + "," + str(height)
    elif prop == "pixel_size":
        pix_size = renderer.get_pixel_size()
        text = str(pix_size)
    elif prop == "samples_per_pixel":
        n = renderer.get_samples_per_pixel()
        text = str(n)
    return text

def set_global_settings(prop, value):
    if prop == "resolution":
        width, height = value.split(',')
        renderer.set_resolution(width, height)
    elif prop == "pixel_size":
        renderer.set_pixel_size(abs(float(value)))
    elif prop == "samples_per_pixel":
        renderer.set_samples_per_pixel(int(value))
    elif prop == "algorithm":
        renderer.set_rendering_algorithm(value)

    return 1

