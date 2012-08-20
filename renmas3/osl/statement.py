

class Statement:
    def __init__(self):
        pass
    
    def asm_code(self):
        raise NotImplementedError()

#allowed a = b  a, b = spectrums
#allowed a -- vector3, vector4, vector2, float, int
#allowed b -- vector3, vector4, vector2, float, int
#implict conversion just int to float

class StmAssignName(Statement):
    def __init__(self, arg1, arg2):
        self.arg1 = arg1
        self.arg2 = arg2

    def asm_code(self):
        #asm code depentd type of name1 and name2
        # name can be integer, vector, float etc...
        # implicit conversions int to float etc...
        pass

