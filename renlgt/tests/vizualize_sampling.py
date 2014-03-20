
import argparse

from sdl import ImageRGBA
from imldr import load_image, save_image
from renlgt.samplers import RegularSampler, RandomSampler,\
    JitteredSampler, SamplerGenerator


def draw_grid(img, ppx):
    width, height = img.size()
    r = 0
    g = 0
    b = 255
    nlines = height // ppx
    for n in range(nlines):
        j = n * ppx
        for i in range(width):
            img.set_pixel(i, j, r, g, b)
            img.set_pixel(i, j + ppx - 1, r, g, b)
    nlines = width // ppx
    for n in range(nlines):
        i = n * ppx
        for j in range(height):
            img.set_pixel(i, j, r, g, b)
            img.set_pixel(i + ppx - 1, j, r, g, b)


def draw_white_rect(img):
    width, height = img.size()
    for j in range(height):
        for i in range(width):
            img.set_pixel(i, j, 255, 255, 255, 255)


def draw_samples(sampler, spp=None, fname=None, grid=False, resolution=None):
    
    if resolution is None:
        resolution = 10
    else:
        resolution = int(resolution)
    if spp is None:
        spp = 16
    else:
        spp = int(spp)

    if sampler == 'regular':
        sam = RegularSampler(width=resolution, height=resolution)
    elif sampler == 'random':
        sam = RandomSampler(width=resolution, height=resolution, nsamples=spp)
    elif sampler == 'jittered':
        sam = JitteredSampler(width=resolution, height=resolution, nsamples=spp)
    else:
        raise ValueError("Unknown sampler %s" % sampler)

    
    sam_gen = SamplerGenerator(sam)

    # sam.create_shader()
    # sam.prepare_standalone()

    ppx = 32
    width = sam._width * ppx
    height = sam._height * ppx
    img = ImageRGBA(width, height)
    draw_white_rect(img) #beacuse of jpeg format

    if grid:
        draw_grid(img, ppx)

    while True:
        if not sam.has_more_samples():
            break

        while True:
            sample = sam_gen.generate_sample()
            if sample is False:
                break
            x = sample.ix * ppx + int(sample.px * ppx)
            y = sample.iy * ppx + int(sample.py * ppx)
            img.set_pixel(x, y, 255, 0, 0)
        sam.increment_pass()

        if not sam.has_more_samples():
            break

    if fname:
        save_image(fname, img)
    else:
        save_image("sampling.png", img)


parser = argparse.ArgumentParser()
parser.add_argument('-s', '--sampler', required=True)
parser.add_argument('-spp', '--samples_per_pixel')
parser.add_argument('-f', '--filename')
parser.add_argument('-g', '--grid', action="store_true")
parser.add_argument('-r', '--resolution')

args = parser.parse_args()

draw_samples(args.sampler, args.samples_per_pixel, args.filename,
             args.grid, args.resolution)
