

class Shape:
    def __init__(self):
        pass

    def isect(self, ray):
        pass

    def isect_b(self, ray): 
        pass

    # eax = pointer to ray structure
    # ebx = pointer to sphere structure
    # edx = pointer to hitpoint
    @classmethod
    def isect_asm(cls, runtimes, label, assembler):
        pass

    # eax = pointer to ray structure
    # ebx = pointer to sphere structure
    @classmethod
    def isect_asm_b(cls, runtimes, label, assembler):
        pass
    
    def attributes(self):
        pass

    def bbox(self):
        pass

    @classmethod
    def name(cls):
        pass

    def light_sample(self, hitpoint):
        return False

    # eax = pointer to hitpoint
    def light_sample_asm(self, label, assembler, spectrum_struct):
        return None

    #This is method for populate required data in light sample calculation
    def populate_ds(self, ds):
        pass

