
x = 2.0 * xwidth * sample.px - xwidth
y = 2.0 * ywidth * sample.py - ywidth

exp_x = -1.0 * alpha * xwidth * xwidth
vx = exp(exp_x)
exp_x = -1.0 * alpha * x * x
vx = exp(exp_x) - vx
vx = max(0.0, vx)

exp_y = -1.0 * alpha * ywidth * ywidth
vy = exp(exp_y)
exp_y = -1.0 * alpha * y * y
vy = exp(exp_y) - vy
vy = max(0.0, vy)

sample.weight = vx * vy
