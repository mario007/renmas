
from tdasm import Runtime
from renmas3.renderer import Renderer, Project

ren = Renderer()
ren.parse_scene_file('scene1.txt')

runtime = Runtime()
ren._project.sampler.prepare([runtime])
ren.save_project("scene1.proj")

ren.open_project("scene1.proj")
print (ren._project.sampler.width)

runtime = Runtime()
ren._project.sampler.prepare([runtime])



