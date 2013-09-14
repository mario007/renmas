
from renlight.image import ImageRGBA
from renlight.win import show_image_in_window

def draw_rect(img, x, y, width, height, r, g, b, a):
    for j in range(y, y + height):
        for i in range(x, x + width):
            img.set_pixel(i, j, r, g, b, a)

img = ImageRGBA(300, 200)
draw_rect(img, 0, 0, 50, 50, 255, 0, 0, 255)
draw_rect(img, 100, 100, 50, 50, 0, 255, 0, 255)
draw_rect(img, 200, 75, 50, 50, 0, 0, 255, 255)
show_image_in_window(img, fliped=False)

