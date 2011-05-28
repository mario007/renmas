
import renmas
import renmas.core
import renmas.samplers
import renmas.camera
import renmas.maths
import renmas.gui
import renmas.lights
import renmas.interface as ren 

def build_scene():
    ren.create_sphere(0, 0, 0, 3)
    
    shapes = ren.lst_shapes()
    return shapes

build_scene()
col = renmas.core.Spectrum(0.05, 0.05, 0.05) 
pos = renmas.maths.Vector3(10.0, 5.0, 8.0)
plight = renmas.lights.PointLight(pos, col) 

hitpoint = renmas.shapes.HitPoint()
hitpoint.hit_point = renmas.maths.Vector3(0.2, 100.5, 0.8)
print (plight.L(hitpoint))

