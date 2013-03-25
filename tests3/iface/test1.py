
import renmas3
import renmas3.interface

id_ren = renmas3.interface.create_renderer("")

#renmas3.interface.import_scene(args)
fname = '../renderer/scene1.proj'
fname = "F:\\GitRenmas\\renmas\\tests3\\renderer\\scene1.proj"
args = id_ren + "," + fname
renmas3.interface.open_project(args)
renmas3.interface.render(id_ren)

output = renmas3.interface.output_image(id_ren)
print(output)
