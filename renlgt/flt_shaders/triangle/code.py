
x = 2.0 * xwidth * sample.px - xwidth
y = 2.0 * ywidth * sample.py - ywidth

if x < 0.0:
    x = x * -1.0

if y < 0.0:
    y = y * -1.0

tx = xwidth - x
ty = xwidth - y

weight = max(0.0, tx) * max(0.0, ty)
sample.weight = weight
