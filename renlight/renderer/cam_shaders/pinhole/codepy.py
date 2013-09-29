

camera = locals()['camera']
sample = locals()['sample']
ray = locals()['ray']

direction = camera._u * sample.x + camera._v * sample.y - camera._w * camera._distance
direction.normalize()
origin = camera._eye * 1.0  # Note: We multiply just to make a copy of vector
ray.origin = origin
ray.direction = direction
