from math import fabs

def _cross(dest, v1, v2):
    dest[0] = v1[1] * v2[2] - v1[2] * v2[1]
    dest[1] = v1[2] * v2[0] - v1[0] * v2[2]
    dest[2] = v1[0] * v2[1] - v1[1] * v2[0]
    return dest

def _dot(v1, v2):
    return v1[0] *v2[0] + v1[1] * v2[1] + v1[2] * v2[2]

def _sub(dest, v1, v2):
    dest[0] = v1[0] - v2[0]
    dest[1] = v1[1] - v2[1]
    dest[2] = v1[2] - v2[2]
    return dest

def _findminmax(x0, x1, x2, minimum, maximum):

    minimum = maximum = x0

    if x1 < minimum:
        minimum = x1
    if x1 > maximum:
        maximum = x1
    if x2 < minimum:
        minimum = x2
    if x2 > maximum:
        maximum = x2

    return minimum, maximum

def _plane_box_overlap(normal, vert, maxbox):
    X = 0
    Y = 1
    Z = 2
    vmin = [0.0] * 3
    vmax = [0.0] * 3

    for q in range(X, Z+1):
        v = vert[q]
        if normal[q] > 0.0:
            vmin[q] = -maxbox[q] - v
            vmax[q] =  maxbox[q] - v
        else:
            vmin[q] = maxbox[q] - v
            vmax[q] = -maxbox[q] - v

    if _dot(normal, vmin) > 0.0:
        return 0

    if _dot(normal, vmax) >= 0.0:
        return 1

    return 0

#int triBoxOverlap(float boxcenter[3],float boxhalfsize[3],float triverts[3][3])
def tri_box_overlap(boxcenter, boxhalfsize, triverts):
    v0 = [0.0] * 3
    v1 = [0.0] * 3
    v2 = [0.0] * 3
    normal = [0.0] * 3
    e0 = [0.0] * 3
    e1 = [0.0] * 3
    e2 = [0.0] * 3
    X = 0
    Y = 1
    Z = 2

    v0 = _sub(v0, triverts[0], boxcenter)
    v1 = _sub(v1, triverts[1], boxcenter)
    v2 = _sub(v2, triverts[2], boxcenter)
    e0 = _sub(e0, v1, v0)
    e1 = _sub(e1, v2, v1)
    e2 = _sub(e2, v0, v2)

    fex = fabs(e0[X])
    fey = fabs(e0[Y])
    fez = fabs(e0[Z])

    p0 = e0[Z] * v0[Y] - e0[Y] * v0[Z]
    p2 = e0[Z] * v2[Y] - e0[Y] * v2[Z]
    if p0 < p2:
        minimum = p0
        maximum = p2
    else:
        minimum = p2
        maximum = p0

    rad = fez * boxhalfsize[Y] + fey * boxhalfsize[Z]
    if minimum > rad or maximum < -rad:
        return 0

    p0 = -e0[Z] * v0[X] + e0[X] * v0[Z]
    p2 = -e0[Z] * v2[X] + e0[X] * v2[Z]
    if p0 < p2:
        minimum = p0
        maximum = p2
    else:
        minimum = p2
        maximum = p0

    rad = fez * boxhalfsize[X] + fex * boxhalfsize[Z]
    if minimum > rad or maximum < -rad:
        return 0

    p1 = e0[Y] * v1[X] - e0[X] * v1[Y]
    p2 = e0[Y] * v2[X] - e0[X] * v2[Y]
    if p2 < p1:
        minimum = p2
        maximum = p1
    else:
        minimum = p1
        maximum = p2

    rad = fey * boxhalfsize[X] + fex * boxhalfsize[Y]
    if minimum > rad or maximum < -rad:
        return 0

    fex = fabs(e1[X])
    fey = fabs(e1[Y])
    fez = fabs(e1[Z])

    p0 = e1[Z] * v0[Y] - e1[Y] * v0[Z]
    p2 = e1[Z] * v2[Y] - e1[Y] * v2[Z]
    if p0 < p2:
        minimum = p0
        maximum = p2
    else:
        minimum = p2
        maximum = p0

    rad = fez * boxhalfsize[Y] + fey * boxhalfsize[Z]
    if minimum > rad or maximum < -rad:
        return 0

    p0 = -e1[Z] * v0[X] + e1[X] * v0[Z]
    p2 = -e1[Z] * v2[X] + e1[X] * v2[Z]
    if p0 < p2:
        minimum = p0
        maximum = p2
    else:
        minimum = p2
        maximum = p0

    rad = fez * boxhalfsize[X] + fex * boxhalfsize[Z]
    if minimum > rad or maximum < -rad:
        return 0

    p0 = e1[Y] * v0[X] - e1[X] * v0[Y]
    p1 = e1[Y] * v1[X] - e1[X] * v1[Y]
    if p0 < p1:
        minimum = p0
        maximum = p1
    else:
        minimum = p1
        maximum = p0

    rad = fey * boxhalfsize[X] + fex * boxhalfsize[Y]
    if minimum > rad or maximum < -rad:
        return 0

    fex = fabs(e2[X])
    fey = fabs(e2[Y])
    fez = fabs(e2[Z])

    p0 = e2[Z] * v0[Y] - e2[Y] * v0[Z]
    p1 = e2[Z] * v1[Y] - e2[Y] * v1[Z]
    if p0 < p1:
        minimum = p0
        maximum = p1
    else:
        minimum = p1
        maximum = p0

    rad = fez * boxhalfsize[Y] + fey * boxhalfsize[Z]
    if minimum > rad or maximum < -rad:
        return 0

    p0 = -e2[Z] * v0[X] + e2[X] * v0[Z]
    p1 = -e2[Z] * v1[X] + e2[X] * v1[Z]
    if p0 < p1:
        minimum = p0
        maximum = p1
    else:
        minimum = p1
        maximum = p0

    rad = fez * boxhalfsize[X] + fex * boxhalfsize[Z]
    if minimum > rad or maximum < -rad:
        return 0

    p1 = e2[Y] * v1[X] - e2[X] * v1[Y]
    p2 = e2[Y] * v2[X] - e2[X] * v2[Y]
    if p2 < p1:
        minimum = p2
        maximum = p1
    else:
        minimum = p1
        maximum = p2

    rad = fey * boxhalfsize[X] + fex * boxhalfsize[Y]
    if minimum > rad or maximum < -rad:
        return 0

    minimum, maximum = _findminmax(v0[X], v1[X], v2[X], minimum, maximum)

    if minimum > boxhalfsize[X] or maximum < -boxhalfsize[X]:
        return 0

    minimum, maximum = _findminmax(v0[Y], v1[Y], v2[Y], minimum, maximum)
    if minimum > boxhalfsize[Y] or maximum < -boxhalfsize[Y]:
        return 0

    minimum, maximum = _findminmax(v0[Z], v1[Z], v2[Z], minimum, maximum)
    if minimum > boxhalfsize[Z] or maximum < -boxhalfsize[Z]:
        return 0

    normal = _cross(normal, e0, e1)

    if not _plane_box_overlap(normal, v0, boxhalfsize):
        return 0

    # box and triangle overlaps
    return 1

if __name__ == "__main__":
    box_center = (0.0, 0.0, 0.0)
    half_size = (50.0, 50.0, 50.0)
    v1 = (100.0, 0.0, 0.0)
    v2 = (-100.0, 0.0, 0.0)
    v3 = (0.0, 100.0, 0.0)

    print(tri_box_overlap(box_center, half_size, (v1, v2, v3)))

