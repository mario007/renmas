
import time
import renmas2

rnd = renmas2.Renderer()
rnd.prepare()

start = time.clock()
while True:
    ret = rnd.render()
    if not ret: break

end = time.clock()
print(end-start)

