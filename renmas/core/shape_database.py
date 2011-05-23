
import renmas.utils 

class ShapeDatabase:
    def __init__(self):
        self.py_shapes = {} # to speed up creation of assembly structures
        self.asm_shapes = {} # DynamicArrays of assembly structures
        self.lst_shapes = []
        # TODO suport for editing!!!!!!! and deleting
        self.sinc = False # do we need build assembly strucures

    def add_shape(self, shape):
        self.lst_shapes.append(shape)
        self.sinc = False
        if type(shape) not in self.py_shapes:
            self.py_shapes[type(shape)] = [shape] 
        else:
            self.py_shapes[type(shape)].append(shape)

    def create_asm_arrays(self):
        if self.sinc is True: return  
        for key, value in self.py_shapes.items():
            dyn_array = renmas.utils.DynamicArray(key.struct(), len(value))
            for shape in value:
                dyn_array.add_instance(shape.attributes())
            self.asm_shapes[key] = dyn_array
        self.sinc = True

    def shapes(self):
        return self.lst_shapes

