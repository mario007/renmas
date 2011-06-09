

from tdasm import Runtime
import renmas.samplers
from renmas.camera import PinholeCamera
import renmas.interface as ren 
import renmas.utils as util

asm_structs = util.structs("ray", "sample")

ASM = """
#DATA
"""
ASM += asm_structs + """
    sample sp1
    ray r1

    float _xmm[4]

    #CODE
    mov eax, r1
    mov ebx, sp1
    call generate_ray
    movaps oword [_xmm], xmm4

"""

if __name__ == "__main__":

    runtime = Runtime()

    asm = util.get_asm()
    mc = asm.assemble(ASM)
    sample = renmas.samplers.Sample()

    camera = ren.pinhole_camera((14,5.0,0), (0,5.0,0), 250)
    camera.ray_asm(runtime, "generate_ray")

    sample.x = 3.4
    sample.y = 4.5
    ray = camera.ray(sample)
    print(ray)

    ds = runtime.load("test", mc)

    ds["sp1.xyxy"] = (3.4, 4.5, 6.6, 7.7)
   
    runtime.run("test")
    print(ds["r1.dir"])
    print(ds["r1.origin"])

    pass


