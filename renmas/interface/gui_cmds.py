
from .create import prepare_for_rendering, create_tiles, get_tile, get_integrator 
from .create import is_rendering_finished
from .create import get_film
from . import create 

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
    prepare_for_rendering()
    create_tiles()
    #create.prepare_raycast_asm()
    create.prepare_pathtracer_asm()

def render(): #render small part of picture
    # grab next fragmet of picture to renderer 
    # render fragment
    tile = get_tile()
    if tile is None: return False 
    integrator = get_integrator()
    integrator(tile)
    film = get_film()
    film.blt_image_to_buffer()
    return True

def is_finished(): 
    return is_rendering_finished()

#FORMAT is float RGBA - 4byte per color channel- alpha channel is 1.0 
def ptr_image():
    film = get_film()
    if film is None: return -1 
    #addr, pitch = film.image.get_addr()
    addr, pitch = film.frame_buffer.get_addr()
    return addr 
    
def width_image():
    film = get_film()
    if film is None: return -1 
    #width, height = film.image.get_size()
    width, height = film.frame_buffer.get_size()
    return width

def height_image():
    film = get_film()
    if film is None: return -1 
    #width, height = film.image.get_size()
    width, height = film.frame_buffer.get_size()
    return height

def pitch_image():
    film = get_film()
    if film is None: return -1 
    #addr, pitch = film.image.get_addr()
    addr, pitch = film.frame_buffer.get_addr()
    return pitch

def get_property(category, name):
    if (category == "camera"):
        if(name == "eye"):
            eye = create.get_camera().eye
            text = str(eye.x) + "," + str(eye.y) + "," + str(eye.z) 
            return text
    if (category == "camera"):
        if(name == "lookat"):
            lookat = create.get_camera().lookat
            text = str(lookat.x) + "," + str(lookat.y) + "," + str(lookat.z) 
            return text
    if (category == "camera"):
        if(name == "distance"):
            distance = create.get_camera().distance
            return str(distance) 

    return ""

def set_property(category, name, value):
    if (category == "camera"):
        if(name == "eye"):
            camera = create.get_camera()
            x, y, z = value.split(',')
            camera.set_eye(float(x), float(y), float(z))
            return 1

    return 1


