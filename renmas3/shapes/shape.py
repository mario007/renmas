

class Shape:
    def __init__(self):
        pass

    def isect(self, ray):
        raise NotImplementedError()

    def isect_b(self, ray): 
        raise NotImplementedError()

    @classmethod
    def asm_struct(cls):
        raise NotImplementedError()

    def attributes(self):
        raise NotImplementedError()

    # eax = pointer to ray structure
    # ebx = pointer to triangle structure
    # ecx = minimum distance
    # edx = pointer to hitpoint
    @classmethod
    def isect_asm(cls, runtimes, label):
        """In runtimes is generated machine code for ray shape intersection.
           If ray hit shape and distance is less than minimum distance
           than hitpoint structure is populated with information about
           intersection point.
        """
        raise NotImplementedError()

    # eax = pointer to ray structure
    # ebx = pointer to shape structure
    # ecx = minimum distance
    @classmethod
    def isect_asm_b(cls, runtimes, label):
        """In runtimes is generated machine code for ray shape intersection.
           If ray hit shape and sitance is less than minimum distance
           then 1 is returned otherwise 0 i returned.
        """
        raise NotImplementedError()

    @classmethod
    def asm_struct_name(cls):
        """Return struct defintion."""
        raise NotImplementedError()
    
    def bbox(self):
        """Return bounding box around shape."""
        raise NotImplementedError()

    def light_sample(self):
        """Return code, props tuple that is used to create light sample shader!"""
        raise NotImplementedError()

