import os.path
from sdl.image import ImageRGBA

def _read_bin_to_asci_line(f):
    a = b''
    for i in range(5000):
        c = f.read(1)
        d = str(c, "ascii")
        if d =='\r' or d == "\n":
            break
        a += c 
    return str(a, "ascii") 

def load_ppm(fname):

    f = open(fname, 'rb')
    identifier = None
    rx = ry = None
    max_value = None

    while True: #reading header information
        line = _read_bin_to_asci_line(f)
        line.strip()
        if line == '' or line == '#':
            continue
        if identifier is None:
            if line != 'P6':
                raise ValueError("Just P6 format is supported.")
            identifier = line
            continue
        if rx is None:
            words = line.split()
            rx = int(words[0])
            ry = int(words[1])
            if len(words) > 2:
                max_value = int(words[3])
                break #whole header is read
            continue

        if max_value is None:
            max_value = int(line)
            break # whole header is read

    #read raw bytes(pixels)
    img = ImageRGBA(rx, ry)
    for y in range(ry):
        for x in range(rx):
            c = f.read(3)
            yy = y
            yy = ry - y - 1 # filp image??
            img.set_pixel(x, yy, c[0], c[1], c[2])
    f.close()
    return img

def save_ppm(fname, image):
    f = open(fname, 'wb')
    identifier = 'P6\n'.encode('ascii')
    width, height = image.size()
    sz = '%i %i\n' % (width, height)
    sz = sz.encode('ascii')
    f.write(identifier)
    f.write(sz)
    f.write('255\n'.encode('ascii'))
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = image.get_pixel(x, y)
            bb = r.to_bytes(1, 'little') + g.to_bytes(1, 'little') + b.to_bytes(1, 'little')
            f.write(bb)
    f.close()

