
from tdasm import Runtime
from renmas3.base import Float, Integer, Vec3, Vector3
from renmas3.base import load_image, ImagePRGBA
from renmas3.tone import calc_img_props, TmoShader


def cmp_images(img1, img2, places=4):
    width, height = img1.size()
    for y in range(height):
        for x in range(width):
            r1, g1, b1, a1 = img1.get_pixel(x, y)
            r2, g2, b2, a2 = img2.get_pixel(x, y)
            if round(r1-r2, places) != 0:
                return False
            if round(g1-g2, places) != 0:
                return False
            if round(b1-b2, places) != 0:
                return False
    return True

def copy_image(in_img, out_image):
    width, height = in_img.size()
    for y in range(height):
        for x in range(width):
            r1, g1, b1, a1 = in_img.get_pixel(x, y)
            out_image.set_pixel(x, y, r1, g1, b1, a1)

img = load_image('F:/hdr_images/Desk_oBA2.hdr')
print(img)
img_props = calc_img_props(img)
print(img_props)
width, height = img.size()
output_image = ImagePRGBA(width, height)

def tmo_py(props, in_img, out_img):
    pass

code = """
rgb_col = get_rgb(in_img, 25, 25)
key = luminance(rgb_col)
rgb_col = normalize(rgb_col)
"""

props = [Float('key', 0.18), Vec3('rgb_col')]

tmo = TmoShader(code=code, py_code=tmo_py, props=props)
tmo.prepare()
print(tmo.shader._code)
tmo.tmo(img, output_image)
print(tmo.shader.get_value('key'))
print(tmo.shader.get_value('rgb_col'))
r1, g1, b1, a2 = img.get_pixel(25,25)
lum = 0.2126 * r1 + 0.7152 * g1 + 0.0722 * b1
print(img.get_pixel(25,25), lum)
vec = Vector3(r1, g1, b1)
print(vec.normalize())

#copy_image(img, output_image)
print(cmp_images(img, output_image))

