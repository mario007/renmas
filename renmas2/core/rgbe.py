
import os
import os.path
import struct
import math
from .image import ImageFloatRGBA

def _read_bin_to_asci_line(f):
    a = b''
    for i in range(5000):
        c = f.read(1)
        d = str(c, "ascii")
        if d =='\r' or d == "\n":
            break
        a += c 
    return str(a, "ascii") 

class Header:
    def __init__(self):
        self.format = None
        self.exposure = 1.0 
        self.software = None
        self.gamma = 1.0
        self.colorcorr = 1.0
        self.pixaspect = 1.0
        self.red_x = 0.640
        self.red_y = 0.330
        self.green_x = 0.290
        self.green_y = 0.600
        self.blue_x = 0.150
        self.blue_y = 0.060
        self.white_x = 0.333
        self.white_y = 0.333


def _read_header(f):
    line1 = _read_bin_to_asci_line(f)
    if line1 != "#?RADIANCE": return None
    header = Header()
    while True:
        line = _read_bin_to_asci_line(f)
        if line == "": break
        words = line.split('=')
        if words[0].upper() == "FORMAT":
            header.format = words[1]
        elif words[0].upper() == "EXPOSURE":
            header.exposure = float(words[1])
        elif words[0].upper() == "SOFTWARE":
            header.software = words[1]
        elif words[0].upper() == "GAMMA":
            header.gamma = float(words[1])
        elif words[0].upper() == "COLORCORR":
            header.colorcorr = float(words[1])
        elif words[0].upper() == "PIXASPECT":
            header.pixaspect = float(words[1])
        elif words[0].upper() == "PRIMARIES":
            w = words[1].split()
            header.red_x = float(w[0])
            header.red_y = float(w[1])
            header.green_x = float(w[2])
            header.green_y = float(w[3])
            header.blue_x = float(w[4])
            header.blue_y = float(w[5])
            header.white_x = float(w[6])
            header.white_y = float(w[7])

    return header

def _read_one_scanline(f, scanline_width):
    scanline_buffer = []
    while len(scanline_buffer) < scanline_width:
        buff = f.read(2)
        if buff[0] > 128:
            # run of the same value
            count = buff[0] - 128
            scanline_buffer.extend([int(buff[1])]*count)
        else:
            count = buff[0]
            if count == 0: return None
            scanline_buffer.append(int(buff[1]))
            count -= 1
            if count > 0: #TODO check this map(int, buff2)
                buff2 = f.read(count)
                scanline_buffer.extend(tuple(map(int, buff2)))

    return scanline_buffer

def _convert_scanline_to_pixels(red, green, blue, exponent, y, img):
    max_r = 0.0
    max_g = 0.0
    max_b = 0.0
    for i in range(len(red)):
        r = red[i]
        g = green[i]
        b = blue[i]
        e = math.pow(2.0, exponent[i] - 128) / 256.0
        r = (r + 0.5) * e
        g = (g + 0.5) * e
        b = (b + 0.5) * e
        img.set_pixel(i, y, r, g, b)


def _read_scanlines(f, header, width, height):
    if width < 8 or width > 32767:
        pass # read uncompressed image
    max_gg = 0.0
    img = ImageFloatRGBA(width, height)
    for i in range(height):
        rgbe = f.read(4)
        if int(rgbe[0]) != 2 or int(rgbe[1]) != 2 or bool(rgbe[2] & 0x80):
            #this file is not run legnth encode
            #read uncompressed image
            return None
        scanline_width = int(int(rgbe[2]) << 8 | rgbe[3]) 
        if scanline_width != width:
            return None
        red_scanline = _read_one_scanline(f, scanline_width)
        green_scanline = _read_one_scanline(f, scanline_width)
        blue_scanline = _read_one_scanline(f, scanline_width)
        exponent = _read_one_scanline(f, scanline_width)
    
        _convert_scanline_to_pixels(red_scanline, green_scanline, blue_scanline, exponent, i, img)
    return img



def load_rgbe(fname):
    if not os.path.exists(fname): return False
    f = open(fname, 'rb')
    header = _read_header(f)
    if header is None: return None

    line = _read_bin_to_asci_line(f)
    words = line.split()
    if words[0] == "-Y" and words[2] == "+X":
        image = _read_scanlines(f, header, int(words[3]), int(words[1]))
        return image
    return None 

