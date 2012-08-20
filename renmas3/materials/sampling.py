
class BRDFSampling:
    def __init__(self):
        pass

    def next_direction(self, sp):
        pass

    # eax - pointer to hitpoint
    # hitpoint.wi -- must be returned next direction
    def next_direction_asm(self, runtimes, assembler, spectrum_struct):
        pass

    def next_direction_asm_label(self, runtimes):
        pass

    def pdf(self, sp):
        pass

    # eax - pointer to hitpoint
    # xmm0 - returned value
    def pdf_asm(self, runtimes, assembler, spectrum_struct):
        pass

    def pdf_asm_label(self, runtimes):
        pass

class BTDFSampling:
    def __init__(self):
        pass

    def next_direction(self, sp):
        pass

    # eax - pointer to hitpoint
    # hitpoint.wi -- must be returned next direction
    def next_direction_asm(self, runtimes, assembler, spectrum_struct):
        pass

    def next_direction_asm_label(self, runtimes):
        pass

    def pdf(self, sp):
        pass

    # eax - pointer to hitpoint
    # xmm0 - returned value
    def pdf_asm(self, runtimes, assembler, spectrum_struct):
        pass

    def pdf_asm_label(self, runtimes):
        pass

