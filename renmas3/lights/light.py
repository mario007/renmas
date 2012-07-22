

class Light:
    def __init__(self):
        pass

    def L(self, shadepoint):
        raise NotImplementedError()

    def L_asm(self, runtimes, assembler, structures):
        raise NotImplementedError()

    def convert_spectrums(self, mgr):
        pass

class EnvironmentLight:
    def __init__(self):
        pass

    def L(self, shadepoint):
        raise NotImplementedError()

    def L_asm(self, runtimes, assembler, structures):
        raise NotImplementedError()

    def Le(self, direction):
        raise NotImplementedError()

    # in xmm0 is direction of ray
    # return spectrum in desired direction
    def Le_asm(self, runtimes, assembler, structures, label):
        raise NotImplementedError()

    def convert_spectrums(self, mgr):
        pass

