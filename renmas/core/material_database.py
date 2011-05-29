
import renmas.utils

class MaterialDatabase:
    def __init__(self):
        self.lst_materials = []
        self.mat_names = {}
        self.mat_idx = {}
        pass

    def add_material(self, name, material):
        self.mat_names[name] = (material, len(self.lst_materials))
        self.mat_idx[len(self.lst_materials)] = material
        self.lst_materials.append(material)

    def mat(self, name):
        return self.mat_names[name][0]

    def material_idx(self, idx):
        return self.mat_idx[idx]

    def get_idx(self, name):
        return self.mat_names[name][1]

    #generate machine code for all materials in database
    #create dynamic array for materials where are pointers to brdf functions
    def gen_asm(self, runtime):
        pass

