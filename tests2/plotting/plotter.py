
from renmas2.core import save_image, ImageRGBA

class Plotter:
    def __init__(self, width, height, wf, wh):
        self.width = width
        self.height = height
        self.wf = wf
        self.wh = wh
        self.kw = float(width) / wf
        self.kh = float(height) / wh
        self._back_r = 255 
        self._back_g = 255
        self._back_b = 255 
        self._plot_r = 255 
        self._plot_g = 0 
        self._plot_b = 0 
        self.img = ImageRGBA(width, height)

    def set_background(self, r, g, b):
        self._back_r = r 
        self._back_g = g 
        self._back_b = b 

    def plot_color(self, r, g, b):
        self._plot_r = 255 
        self._plot_g = 0 
        self._plot_b = 0 

    def draw_point(self, x, y, color=None):
        imgx = int(self.kw * x)
        imgy = int(self.kh * y)
        if color is None:
            self.img.set_pixel(imgx, imgy, self._plot_r, self._plot_g, self._plot_b)
        else:
            r, g, b = color
            self.img.set_pixel(imgx, imgy, r, g, b)

    def reset(self): # draw background color
        width, height = self.img.get_size() 
        for y in range(height):
            for x in range(width):
                self.img.set_pixel(x, y, self._back_r, self._back_g, self._back_b)

    def save(self, fname):
        save_image(fname, self.img)

if __name__ == "__main__":
    ploter = Plotter(200, 200, 1.0, 1.0)
    ploter.reset()

    x = 0.3
    for i in range(100):
        ploter.draw_point(x, 0.6)
        x += 0.004
        print(x)

    ploter.save("crno.png")

