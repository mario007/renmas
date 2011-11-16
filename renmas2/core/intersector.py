
class Intersector:
    def __init__(self):
        self.strategy = 'grid' #or linear ###tip: enum type

    def add(self, name, shape):
        pass

    def remove(self, name):
        pass

    def address_off(self, shape):
        pass

    def isect(self, ray): #intersection ray with scene
        pass

    def isect_asm(self, runtimes, label):
        pass

    def visibility_asm(self, runtimes, label):
        pass

    def prepare(self): #build acceleration structure
        if self.strategy == 'grid':
            pass #build grid
        else:
            pass #linear

    def set_strategy(self, strategy):
        if strategy == 'grid':
            self.strategy = strategy
        else:
            self.strategy = 'linear'

