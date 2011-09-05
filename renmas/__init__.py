
import renmas.core

scene = renmas.core.Scene()
geometry = renmas.core.ShapeDatabase()

mat_db = renmas.core.MaterialDatabase()
light_db = renmas.core.LightDatabase()

import renmas.integrators

renderer = renmas.core.Renderer()

ren = renmas.core.RendererUtils(renderer)

log = renmas.core.log

