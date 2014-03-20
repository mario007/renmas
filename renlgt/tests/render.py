
import time
import os.path
import argparse

from sdl.blt_floatrgba import blt_prgba_to_rgba, ImageRGBA
from imldr import save_image
from renlgt import Renderer


def render(filename, output=None, integrator=None, tmo=True):
    ren = Renderer()
    if integrator is not None:
        ren.integrator.load(integrator)
    print("Begin of loading %s" % filename)
    start = time.clock()
    ren.load(filename)
    elapsed = time.clock() - start
    print("Loading scene took %f seconds" % elapsed)

    print("Begin preparing scene for rendering")
    start = time.clock()
    ren.prepare()
    elapsed = time.clock() - start
    print("Preparation of scene took %f seconds" % elapsed)
   
    total_time = 0.0
    iteration = 0
    while True:
        start = time.clock()
        ret = ren.render()
        elapsed = time.clock() - start
        total_time += elapsed
        iteration += 1
        print("Rendering of iteration %i took %f seconds" % (iteration, elapsed))
        if ret:  # We finished rendering all samples 
            break;
    print("Total rendering time took %f seconds." % total_time)

    if output is None:
        output = 'Unknown.jpeg'

    name, ext = os.path.splitext(output)
    if ext in ('.rgbe', '.exr'):
        save_image(output, ren._hdr_buffer)
    else:
        width, height = ren._hdr_buffer.size()
        new_img = ImageRGBA(width, height)
        if tmo:
            print("Tone mapping is in progress!")
            start = time.clock()
            ren.tmo()
            elapsed = time.clock() - start
            print("Tone mapping took %f seconds!" % elapsed)
            blt_prgba_to_rgba(ren._hdr_output, new_img)
        else:
            blt_prgba_to_rgba(ren._hdr_buffer, new_img)
        save_image(output, new_img)


parser = argparse.ArgumentParser()
parser.add_argument('-f', '--filename', required=True)
parser.add_argument('-o', '--output')
parser.add_argument('-i', '--integrator')
parser.add_argument('-t', '--tmo', action="store_true")

args = parser.parse_args()

render(args.filename, args.output, args.integrator, not args.tmo)
