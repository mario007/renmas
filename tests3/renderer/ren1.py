import time

import renmas3
import renmas3.core
from renmas3.win32 import show_image_in_window

start = time.clock()
ren = renmas3.core.Renderer()
irender = renmas3.core.IRender(ren)
end = time.clock()
print(end-start)

filename = 'I:\\GitRENMAS\\tests3\\renderer\\sphere1.py'
filename = 'E:\\GitRENMAS\\renmas\\tests3\\renderer\\sphere1.py'

exec(compile(open(filename).read(), filename, 'exec'), dict(locals()), dict(globals()))

ren.prepare()

start = time.clock()
ren.render()
ren.tone_map()
end = time.clock()
print(end-start)
show_image_in_window(ren._image)

