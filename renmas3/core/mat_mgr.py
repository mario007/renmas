from .material import Material

class MaterialManager:
    def __init__(self):

        # containers for materials
        self._materials = {}
        self._materials_lst = []
        self._materials_idx = {}

    @property
    def materials(self):
        return self._materials_lst

    def material_idx(self, name):
        if name in self._materials:
            return self._materials[name][1]
        return None
    
    def material_name(self, idx):
        material = self._materials_idx[idx]
        for key, value in self._materials.items():
            if value[0] == material:
                return key
        return None

    def material(self, name):
        if name in self._materials:
            return self._materials[name][0]
        return None
   
    def material_names(self):
        return self._materials.keys()

    def convert_spectrums(self, col_mgr):
        for m in self._materials_lst:
            m.convert_spectrums(col_mgr)

    def add(self, name, obj): #material
        if isinstance(obj, Material): #TODO check if material allready exist
            if name in self._materials:
                return #Material allread exist -- put information in log
            self._materials[name] = (obj, len(self._materials_lst)) 
            self._materials_idx[len(self._materials_lst)] = obj
            self._materials_lst.append(obj)
