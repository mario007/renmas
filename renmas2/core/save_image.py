
import os
import os.path
import imload

def save_image(fname, img):
    
    addr, pitch = img.get_addr()
    width, height = img.get_size()
    imload.SaveRGBAToPNG(fname, addr, width, height)

