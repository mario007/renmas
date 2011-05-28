
from renmas.samplers import RegularSampler, RandomSampler
from renmas.samplers import Sample 
from tdasm import Runtime
import renmas.utils as util



def print_random(rnd, runtime, ds):
    sample = Sample()
    while True:
        sam = rnd.get_sample(sample)
        runtime.run("test")
        print_sample(ds, "sam")
        if sam is None: break
        print ("Python = (", sample.ix, sample.x, ")",  " (", sample.iy, sample.y, ")")
        print("===============")
    print("===============")
    runtime.run("test")
    print_sample(ds, "sam")
    runtime.run("test")
    print_sample(ds, "sam")
    runtime.run("test")
    print_sample(ds, "sam")

ASM = """
    #DATA
"""
ASM += util.structs("sample") + """
    sample sam 
    uint32 have

    #CODE

    mov eax, sam 

    call get_sample
    mov dword [have], eax
    #END
"""

def print_sample(ds, name):
    x, y, temp1, temp2 = ds[name + ".xyxy"]
    print("ASM =   ", "(",ds[name+".ix"], x, ") (", ds[name+".iy"], y, ") have =", ds["have"])

if __name__ == "__main__":
    
    runtime = Runtime()

    rnd = RandomSampler(2, 2, n=2)
    rnd.get_sample_asm(runtime, "get_sample")

    assembler = util.get_asm()
    mc = assembler.assemble(ASM)
    ds = runtime.load("test", mc)

    print_random(rnd, runtime, ds)

