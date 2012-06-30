
import time
from renmas3.loaders import load_image, save_image, register_image_writer

#image = load_image("leaf.tga")
#image = load_image("flag_t32.tga")
#image = load_image("xing_b32.tga")
image = load_image("rle.tga")
print(image)
if image is not None:
    start = time.clock()
    img2 = image.to_bgra()
    end = time.clock()
    print(img2)
    print("bili", end-start)



