#NOTE: this is shader code not python code
# Logaritmic tone mapping operator with gamma correction
# input_image, output_image are implict parameter to shader


# first step is to calculate some image statistics
# calculation of maximum luminance
width = input_image.width
height = input_image.height
i = 0
j = 0
max_luminance = 0.0
while j < height:
    i = 0
    while i < width:
        val = get_rgba(input_image, i, j)
        lum = luminance(val)
        max_luminance = max(max_luminance, lum)
        i = i + 1
    j = j + 1

inv_gamma = 1.0 / gamma
inv_gamma = float4(inv_gamma, inv_gamma, inv_gamma, inv_gamma)

denom = k * max_luminance + 1.0
denom = log(denom) / 2.303 #2.303 conversion from ln to log10

j = 0
while j < height:
    i = 0
    while i < width:
        val = get_rgba(input_image, i, j)
        lw = luminance(val)
        tmp = q * lw + 1.0
        #tmp = log(tmp) / 2.303 #2.303 conversion form ln to log10
        tmp = log(tmp) * 0.4342162 #1.0/2.303 conversion form ln to log10
        ld = tmp / denom
        compression = ld / lw
        val = val * compression

        #gama correction
        val = pow(val, inv_gamma)

        val = float4(val[0], val[1], val[2], 0.99)
        set_rgba(output_image, i, j, val)
        i = i + 1
    j = j + 1

