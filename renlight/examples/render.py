
import time
from tdasm import Runtime

from renlight.vector import Vector3
from renlight.renderer.sampler import Sampler
from renlight.renderer.camera import Camera
from renlight.renderer.integrator import Integrator
from renlight.renderer.sphere import Sphere
from renlight.renderer.linear import LinearIsect
from renlight.renderer.shp_mgr import ShapeManager
from renlight.image import ImagePRGBA, ImageRGBA
from renlight.renderer.blt_floatrgba import blt_prgba_to_rgba
from renlight.win import show_image_in_window

if __name__ == "__main__":

    runtimes = [Runtime()]
    sampler = Sampler()
    sampler.set_resolution(1024, 768)
    sampler.load('regular')

    eye = Vector3(0.0, 10.0, 5.0)
    lookat = Vector3(0.0, 0.0, 0.0)
    distance = 100.0
    camera = Camera(eye, lookat, distance)
    camera.load('pinhole')

    #intersection
    mgr = ShapeManager()
    sphere = Sphere(Vector3(0.0, 0.0, 0.0), 2.0, 0)
    mgr.add('sph1', sphere)

    isector = LinearIsect(mgr)
    isector.compile()
    isector.prepare(runtimes)

    ###################

    integrator = Integrator()
    integrator.load('isect_shader')

    sampler.compile()
    camera.compile()
    sampler.prepare(runtimes)
    camera.prepare(runtimes)

    integrator.compile([sampler.shader, camera.shader, isector.shader])
    integrator.prepare(runtimes)
    img = ImagePRGBA(1024, 768)
    integrator.shader.set_value('image', img)

    start = time.clock()
    integrator.execute()
    end = time.clock()
    print("Rendering time:", end-start)

    img2 = ImageRGBA(1024, 768)
    blt_prgba_to_rgba(img, img2)
    show_image_in_window(img2, fliped=False)
