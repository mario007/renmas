
import renmas2

renderer = renmas2.Renderer()
spd = renderer.spd 

#ret = spd.load("light", "A")
#ret = spd.load("real_object", "cotton_shirt")
ret = spd.load("metal", "silver")
print(ret)

