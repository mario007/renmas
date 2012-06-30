
import os.path
from struct import unpack, pack
from io import SEEK_CUR

from ..core import ImageRGBA

def _add_pixel(image, x, y, nbytes, data):
    if nbytes == 4:
        image.set_pixel(x, y, data[2], data[1], data[0], data[3])
    elif nbytes == 3:
        image.set_pixel(x, y, data[2], data[1], data[0])
    elif nbytes == 2:
        r = (data[1] & 0x7C) << 1
        g = ((data[1] & 0x03) << 6) | ((data[0] & 0xE0) >> 2)
        b = (data[0] & 0x1F) << 3
        image.set_pixel(x, y, r, g, b)

def _read_uncompressed(f, width, height, nbytes, image):
    for j in range(height):
        for i in range(width):
            b = f.read(nbytes)
            if len(b) != nbytes: return None # unexpected end of file
            _add_pixel(image, i, j, nbytes, b)
    return image

def _read_compressed(f, width, height, nbytes, image):

    i = j = 0

    while j < height:
        b = f.read(nbytes + 1)
        if len(b) != nbytes+1: return None # unexpected end of file
        _add_pixel(image, i, j, nbytes, b[1:])
        i += 1
        if i == width: i = 0; j += 1
        c = b[0] & 0x7F
        r = b[0] & 0x80 
        if r: # RLE chunk
            for m in range(c):
                _add_pixel(image, i, j, nbytes, b[1:])
                i += 1
                if i == width: i = 0; j += 1
        else: # Normal chunk
            for m in range(c):
                b = f.read(nbytes)
                if len(b) != nbytes: return None # unexpected end of file
                _add_pixel(image, i, j, nbytes, b)
                i += 1
                if i == width: i = 0; j += 1
    return image

def load_tga(fname):
    if not os.path.isfile(fname): return None #file doesn't exists

    f = open(fname, 'rb')

    # READ HEADER of IMAGE
    id_length = f.read(1)[0]
    color_map_type = f.read(1)[0] # 0 - no color map in image, 1 - color map is included

    # 0 - no image data, 1 - Uncompressed(color-map) image, 2 - Uncompressed(true color) image
    # 3 - Uncompressed Black and White image, 9 - RLE color mapped image, 10 - RLE true color, 11 - RLE black and white
    image_type = f.read(1)[0] # 0 - no image data, 1 - Uncompressed(color-map) image, 2 - Uncompressed(true color) image

    color_map_origin = unpack('h', f.read(2))[0] 
    color_map_length = unpack('h', f.read(2))[0] 
    color_map_entry_size = f.read(1)[0]

    x_origin = unpack('h', f.read(2))[0] 
    y_origin = unpack('h', f.read(2))[0] 
    width = unpack('h', f.read(2))[0] 
    height = unpack('h', f.read(2))[0] 
    pixel_depth = f.read(1)[0]
    image_descriptor = f.read(1)[0]

    # CHECK IF LOADER SUPPORT IMAGE
    if image_type != 2 and image_type != 10: return None # only true color is supported 
    if pixel_depth != 16 and pixel_depth != 24 and pixel_depth != 32: return None
    if color_map_type !=0 and color_map_type != 1: return None

    # SKIP OVER UNNECESSARY BYTES
    skip = id_length + color_map_type * color_map_length
    f.seek(skip, SEEK_CUR)

    # TODO -- image descriptor --- ordering of pixel, bottom left, top left etc...

    #READ IMAGE BYTES
    image = ImageRGBA(width, height)

    if image_type == 2:
        ret = _read_uncompressed(f, width, height, pixel_depth//8, image)
    elif image_type == 10:
        ret = _read_compressed(f, width, height, pixel_depth//8, image)

    f.close()
    return ret


def save_tga(fname, image):
    try: # maybe some protection is on file system and new file cannot be created
        f = open(fname, 'wb')
    except:
        return False 

    #WRITE HEADER
    b = bytearray([0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    f.write(b)
    width, height = image.size()
    b =  pack('hh', width, height)
    f.write(b)
    f.write(bytearray([32, 0]))

    #WRITE BYTES 
    for j in range(height):
        for i in range(width):
            r, g, b, a = image.get_pixel(i, j)
            f.write(bytearray([b, g, r, a]))
    f.close()
    return True



