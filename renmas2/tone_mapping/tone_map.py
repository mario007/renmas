
class ImageProps:
    def __init__(self, red_av, green_av, blue_av, luminance_av, luminance_min, luminance_max):
        self.red_av = red_av
        self.green_av = green_av
        self.blue_av = blue_av
        self.luminance_av = luminance_av
        self.luminance_min = luminance_min
        self.luminance_max = luminance_max

class ToneMapping:
    def __init__(self):
        pass


    def tone_map(self, in_picture, out_picture, x, y, width, height):
        pass


