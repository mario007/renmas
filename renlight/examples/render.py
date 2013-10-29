
import time
from tdasm import Runtime

from renlight.vector import Vector3
from renlight.renderer.sampler import Sampler
from renlight.renderer.camera import Camera
from renlight.renderer.integrator import Integrator

if __name__ == "__main__":

    sampler = Sampler()
    sampler.set_resolution(1024, 768)
    sampler.load('regular')

    eye = Vector3(0.0, 10.0, 5.0)
    lookat = Vector3(0.0, 0.0, 0.0)
    distance = 100.0
    camera = Camera(eye, lookat, distance)
    camera.load('pinhole')

    integrator = Integrator()
    integrator.load('isect_shader')

    runtimes = [Runtime()]

    integrator.compile([sampler.shader, camera.shader])
    integrator.prepare(runtimes)

    start = time.clock()
    integrator.execute()
    end = time.clock()
    print(end-start)
