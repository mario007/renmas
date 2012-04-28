

class Sampling:
    def __init__(self):
        pass

    def next_direction(self, hitpoint):
        pass

    # eax - pointer to hitpoint
    # hitpoint.wi -- must be returned next direction
    # hitpoint.ndotwi -- also must be computed -- for little extra performance
    def next_direction_asm(self, runtimes, structures, assembler):
        pass

    def pdf(self, hitpoint):
        pass

    # eax - pointer to hitpoint
    # xmm0 - returned value
    def pdf_asm(self):
        pass

    #populate ds
    def pdf_ds(self, ds):
        pass

class BTDFSampling:
    def __init__(self):
        pass

    def next_direction(self, hitpoint):
        pass

    # eax - pointer to hitpoint
    # hitpoint.wi -- must be returned next direction
    # hitpoint.ndotwi -- also must be computed -- for little extra performance
    def next_direction_asm(self, runtimes, structures, assembler):
        pass

    def pdf(self, hitpoint):
        pass

    # eax - pointer to hitpoint
    # xmm0 - returned value
    def pdf_asm(self):
        pass

    #populate ds
    def pdf_ds(self, ds):
        pass

