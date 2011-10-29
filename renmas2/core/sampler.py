import math
from .dynamic_array import DynamicArray
from .structures import Structures
import x86
from tdasm import Runtime
from ..macros import macro_call, assembler

class Tile:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.lst_tiles = None

    #you can recive less tiles than requested!!! Be cerful to acount for this 
    def split(self, n): #split tile to n mini-tiles
        hp = int(float(self.height) / n) + 1
        self.lst_tiles = []
        for k in range(self.y, self.y+self.height, hp):
            nh = hp
            if k > self.y + self.height - hp: nh = self.y + self.height - k
            self.lst_tiles.append(Tile(self.x, k, self.width, nh))


class Sampler:
    def __init__(self, width, height, n=1, pixel=1.0):
        self.pixel_size = float(pixel)
        self.n = int(n)
        self.ncore = 1 # number of cores - multithreading
        self.python = True # python or assembly to generate samples 
        self._runtime_arr = None # array of runtimes
        self._exe_address = None # tuple of address - multi threading
        self.end_sampling = False # mark that we are finished with samplings  
        self._batch_samples = 100000 #max number of samples to generate in array 
        self._sample_array = None
        self.structures = Structures()

        self.resolution(width, height)
        self._allocate_array()

    def _allocate_array(self):
        self._sample_array = DynamicArray(self.structures.get_compiled_struct('sample'))
        self._sample_array.add_default_instances(self._batch_samples)

    def set_max_samples(self, n):
        self.batch_samples = abs(int(n))
        self._allocate_array()
        self._generate_tiles()

    def python_version(self, version=True):
        self.python = version 
        self._generate_tiles()
        if not version:
            self._build_runtimes()

    def _get_assembly_code(self):
        raise NotImplementedError()

    def _populate_data(self, ds, tile, addr=None):
        raise NotImplementedError()

    def _generate_samples_python(self):
        raise NotImplementedError()

    def _build_runtimes(self):
        if self.python: return #python will generate samples
        self._runtime_arr = []
        adr = []
        for n in range(self.ncore):
            run = Runtime()
            macro_call.set_runtimes([run])
            mc = assembler.assemble(self._get_assembly_code())
            #mc.print_machine_code()
            run.load('generate_samples', mc)
            self._runtime_arr.append(run)
            adr.append(run.address_module('generate_samples'))
        self._exe_address = tuple(adr)
        
    def set_ncore(self, n):
        nc = abs(int(n))
        if nc > 32: nc = 32 #max number of threads
        self.ncore = nc
        self._generate_tiles()
        self._build_runtimes()

    def resolution(self, width, height):
        self.width = width
        self.height = height
        self._generate_tiles()

    def pixel_size(self, size):
        self.pixel_size = float(size)
        self._populate_ds()

    def get_pixel_size(self):
        return self.pixel_size

    def reset(self):
        self.end_sampling = False # mark that we are finished with samplings 
        self._lst_tiles = list(self.tiles)

    def nsamples(self):
        return self.n 

    def set_samples_per_pixel(self, num):
        self.n = int(num) 
        self._generate_tiles()

    def show_sample(self, i):
        sd = self._sample_array.get_instance(i)
        ix = sd['ix']
        iy = sd['iy']
        x, y, dummy, dummy = sd['xyxy']
        weight = sd['weight']
        print('x= %i sx= %f, y= %i sy= %f weight= %f' % (ix, x, iy, y, weight))


    def _generate_tiles(self):

        width = self.width
        height = self.height

        w = h = int(math.sqrt(self._batch_samples / self.n))
        #w = h = 50
        sx = sy = 0
        xcoords = []
        ycoords = []
        tiles = []
        while sx < width:
            xcoords.append(sx)
            sx += w
        last_w = width - (sx - w) 
        while sy < height:
            ycoords.append(sy)
            sy += h
        last_h = height - (sy - h)

        for i in xcoords:
            for j in ycoords:
                tw = w
                th = h
                if i == xcoords[-1]:
                    tw = last_w
                if j == ycoords[-1]:
                    th = last_h
                t = Tile(i, j, tw, th)
                t.split(self.ncore) #multithreading
                tiles.append(t)

        self.tiles = tiles
        self._lst_tiles = list(self.tiles)

    def _generate_samples_asm(self, tile):
        if self._runtime_arr is None:
            raise ValueError('We dont have Runtime objects!')
        if self.ncore == 1:
            r = self._runtime_arr[0]
            ds = r.get_datasection('generate_samples')
            self._populate_data(ds, tile)
            x86.ExecuteModules(self._exe_address)
        else: 
            addr = self._sample_array.get_addr()
            sample_size = self._sample_array.obj_size()
            for idx in range(len(tile.lst_tiles)):
                r = self._runtime_arr[idx]
                mt = tile.lst_tiles[idx]
                ds = r.get_datasection('generate_samples')
                self._populate_data(ds, mt, addr)
                addr += (mt.width * mt.height * self.n * sample_size) 
            x86.ExecuteModules(self._exe_address[0:len(tile.lst_tiles)])

        req_samples = tile.width * tile.height * self.n
        return req_samples

    def generate_samples(self):
        if self.end_sampling: return 0
        try:
            tile = self._lst_tiles.pop()
            if self.python: #assembly or python to generate samples
                return self._generate_samples_python(tile)
            else:
                return self._generate_samples_asm(tile)
        except IndexError:
            self.end_sampling = True
            return 0 # All tiles are rendererd

