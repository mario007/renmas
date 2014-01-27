
import unittest
from renlgt.camera import Camera
from sdl import Vector3, Ray
from renlgt.sample import Sample


class CameraTest(unittest.TestCase):

    def generate_pinhole_ray(self, camera, sample):

        direction = camera._u * sample.x + camera._v *\
            sample.y - camera._w * camera._distance

        direction.normalize()
        eye = camera._eye
        origin = Vector3(eye.x, eye.y, eye.z)
        return Ray(origin, direction)

    def test_pinhole(self):
        cam = Camera(eye=Vector3(5.0, 5.0, 5.0),
                     lookat=Vector3(0.0, 0.0, 0.0), distance=200)
        cam.load('pinhole')
        cam.prepare_standalone()

        sample = Sample(x=2.14, y=3.33, px=0.6, py=0.7, ix=2, iy=2, weight=1.0)
        r1 = cam.generate_ray(sample)
        r2 = self.generate_pinhole_ray(cam, sample)

        self.assertAlmostEqual(r1.origin.x, r2.origin.x)
        self.assertAlmostEqual(r1.origin.y, r2.origin.y)
        self.assertAlmostEqual(r1.origin.z, r2.origin.z)

        self.assertAlmostEqual(r1.direction.x, r2.direction.x)
        self.assertAlmostEqual(r1.direction.y, r2.direction.y)
        self.assertAlmostEqual(r1.direction.z, r2.direction.z)

if __name__ == "__main__":
    unittest.main()
