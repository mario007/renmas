


if cury == endy:
    return 0

tmp = curx - width * 0.5
tmp2 = cury - height * 0.5

sample.x = pixel_size * (tmp + 0.5)
sample.y = pixel_size * (tmp2 + 0.5)
sample.ix = curx
sample.iy = cury
sample.weight = 1.0

curx = curx + 1
if curx == endx:
    curx = tile.x
    cury = cury + 1
return 1

