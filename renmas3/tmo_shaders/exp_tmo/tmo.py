#NOTE: this is shader code not python code
# Exponential tone mapping operator with gamma correction
# input_image, output_image are implict parameter to shader


# first step is to calculate some image statistics
# calculation of logaritmic average luminance
width = input_image.width
height = input_image.height
i = 0
j = 0
epsilon = 0.00001
acum = 0.0
while j < height:
    i = 0
    while i < width:
        val = get_rgba(input_image, i, j)
        lum = luminance(val) + epsilon
        acum = acum + log(lum)
        i = i + 1
    j = j + 1

npixels = width * height
acum = acum / npixels

log_av = exp(acum)
ratio = (q / k) * -1.0

inv_gamma = 1.0 / gamma
inv_gamma = float4(inv_gamma, inv_gamma, inv_gamma, inv_gamma)

j = 0
while j < height:
    i = 0
    while i < width:
        val = get_rgba(input_image, i, j)
        lw = luminance(val)
        temp = ratio * lw / log_av
        ld = 1.0 - exp(temp)
        compression = ld / lw
        val = val * compression

        #gama correction
        val = pow(val, inv_gamma)

        val = float4(val[0], val[1], val[2], 0.99)
        set_rgba(output_image, i, j, val)
        i = i + 1
    j = j + 1

