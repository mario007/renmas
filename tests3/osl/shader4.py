
from tdasm import Runtime
import renmas3.base
from renmas3.base import create_shader, create_user_type
from renmas3.base import register_user_type
from renmas3.base import arg_map, arg_list
from renmas3.base import Tile
from renmas3.base import Vector3

sample = create_user_type(typ="sample", fields=[('x', 0.0), ('y', 0.0), 
                                    ('ix', 0), ('iy', 0), ('weight', 1.0)])
register_user_type(sample)

def get_sample(self):
    self._curx += 1
    if self._curx == self._endx:
        self._curx = self._tile.x
        self._cury += 1
        if self._cury == self._endy:
            return None
    
    x = self._pixel_size * (self._curx + self._w2)  
    y = self._pixel_size * (self._cury + self._h2)
    return Sample(x, y, self._curx, self._cury, 1.0)

code2 = """
#input arg is sample structure, name = sam
curx = curx + 1
if curx == endx:
    curx = tilex
    cury = cury + 1
    if cury == endy:
        return 0
#x = pixel_size * (curx + w2)
#y = pixel_size * (cury + h2)

x = pixel_size * (w2 + curx)
y = pixel_size * (w2 + cury)
sam.x = x
sam.y = y
sam.ix = curx
sam.iy = cury
return 1
"""

args1 = arg_map([('endx', 0), ('endy', 0), ('tilex', 0), ('tiley', 0),
    ('pixel_size', 1.0), ('curx', 0), ('cury', 0), ('w2', 0.0), ('h2', 0.0)])
args2 = arg_list([('sam', sample)])
sample_shader = create_shader("generate_sample", code2, args1, args2, func=True)
#print(sample_shader._code)


arg_map1 = arg_map([('x', 0.0)])
code = """
sam = sample()
ret = 1
while ret != 0:
    ret = generate_sample(sam)
x = sam.y
"""

runtimes = [Runtime()]
shader = create_shader("test", code, arg_map1, shaders=[sample_shader])
#print(shader._code)
shader.prepare(runtimes)

tile = Tile(0, 0, 10, 10)
width = 100
height = 100
sample_shader.set_value('endx', tile.x + tile.width)
sample_shader.set_value('endy', tile.y + tile.height)
sample_shader.set_value('tilex', tile.x)
sample_shader.set_value('tiley', tile.y)
sample_shader.set_value('pixel_size', 1.0)
sample_shader.set_value('curx', tile.x - 1)
sample_shader.set_value('cury', tile.y)
sample_shader.set_value('w2', -float(width) * 0.5 + 0.5)
sample_shader.set_value('h2', -float(height) * 0.5 + 0.5)

shader.execute()

print(shader.get_value('x'))


