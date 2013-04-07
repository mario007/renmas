
import renmas3
import renmas3.interface

fname = '../scenes/cornel4.txt'
fname = '../scenes/sphere1.txt'
id_ren = renmas3.interface.exec_func('create_renderer', '')
renmas3.interface.exec_method(id_ren, 'parse_scene_file', fname)
renmas3.interface.exec_method(id_ren, 'render', '')
print(renmas3.interface.exec_method(id_ren, 'output_image', ''))


