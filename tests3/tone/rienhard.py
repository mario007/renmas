import time
from renmas3.tone import ReinhardOperator, Tmo
from renmas3.base import ImageBGRA, load_image, FileLoader, ImagePRGBA 
from renmas3.win32 import show_image_in_window
from renmas3.utils import blt_prgba_to_bgra
from renmas3.renderer.renderer import create_props

def create_tmo(tmo_shader='exp_tmo'):
    tmo_loader = FileLoader(["F:/GitRenmas/renmas/renmas3/tmo_shaders"])
    contents = tmo_loader.load(tmo_shader, 'props.txt')
    props = create_props(contents)
    contents = tmo_loader.load(tmo_shader, 'tmo.py')
    tmo = Tmo(contents, props)
    return tmo

hdr_image = load_image('Desk_oBA2.hdr')
#hdr_image = load_image('AtriumNight_oA9D.hdr')
width, height = hdr_image.size()
ldr_image = ImagePRGBA(width, height)

output_image = ImageBGRA(width, height)
reinhard = ReinhardOperator()
tmo = create_tmo('log_tmo')

start = time.clock()

#tmo shader
tmo.tone_map(hdr_image, ldr_image)
blt_prgba_to_bgra(ldr_image, output_image)

#old asm implementation
#reinhard.tone_map(hdr_image, output_image)

#without tone mapping
#blt_prgba_to_bgra(hdr_image, output_image)

end = time.clock()
print(end-start)

show_image_in_window(output_image)

