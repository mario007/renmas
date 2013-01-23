
import argparse 
from tdasm import Runtime 
from renmas3.base import Vector3, Ray, BasicShader
from renmas3.base import VertexBuffer, VertexNBuffer, VertexUVBuffer
from renmas3.base import VertexNUVBuffer, TriangleBuffer
from renmas3.shapes import HitPoint, load_meshes, HitPoint, random_in_bbox
from renmas3.shapes import LinearIsect, ShapeManager, Triangle

def create_triangle(v0, v1, v2, n0=None, n1=None, n2=None,
                     uv0=None, uv1=None, uv2=None):

    p0 = Vector3(v0[0], v0[1], v0[2])
    p1 = Vector3(v1[0], v1[1], v1[2])
    p2 = Vector3(v2[0], v2[1], v2[2])
    if n0 is not None:
        n0 = Vector3(n0[0], n0[1], n0[2])
        n1 = Vector3(n1[0], n1[1], n1[2])
        n2 = Vector3(n2[0], n2[1], n2[2])
    if uv0 is not None:
        tu0, tv0 = uv0
        tu1, tv1 = uv1
        tu2, tv2 = uv2
    else:
        tu0 = tv0 = tu1 = tv1 = tu2 = tv2 = None

    t = Triangle(p0, p1, p2, n0=n0, n1=n1, n2=n2, tu0=tu0,
            tv0=tv0, tu1=tu1, tv1=tv1, tu2=tu2, tv2=tv2)
    return t

def populate(mgr, tb, vb):
    counter = 0
    name = "t" + str(id(tb))
    for i in range(tb.size()):
        idx1, idx2, idx3 = tb.get(i)
        if isinstance(vb, VertexBuffer):
            v0 = vb.get(idx1)
            v1 = vb.get(idx2)
            v2 = vb.get(idx3)
            n0 = n1 = n2 = uv0 = uv1 = uv2 = None
        elif isinstance(vb, VertexNBuffer):
            v0, n0 = vb.get(idx1)
            v1, n1 = vb.get(idx2)
            v2, n2 = vb.get(idx3)
            uv0 = uv1 = uv2 = None
        elif isinstance(vb, VertexUVBuffer):
            v0, uv0 = vb.get(idx1)
            v1, uv1 = vb.get(idx2)
            v2, uv2 = vb.get(idx3)
            n0 = n1 = n2 = None
        elif isinstance(vb, VertexNUVBuffer):
            v0, n0, uv0 = vb.get(idx1)
            v1, n1, uv1 = vb.get(idx2)
            v2, n2, uv2 = vb.get(idx3)
        else:
            raise ValueError("Unknown vertex buffer", vb)

        t = create_triangle(v0, v1, v2, n0=n0, n1=n1, n2=n2,
                             uv0=uv0, uv1=uv1, uv2=uv2)
        mgr.add(name+str(counter), t)
        counter += 1

def populate_mgr(mgr, fname):
    meshes = load_meshes(fname)
    for m in meshes:
        populate(mgr, m.tb, m.vb)

def compare(hit, bs, ray):
    if hit is False and bs.shader.get_value('ret') != 0:
        print(ray.origin)
        print(ray.dir)
        raise ValueError("Intersection error!")

    if hit is False:
        return

    r1 = hit.t
    r2 = bs.shader.get_value('hit.t')
    if round(r1-r2, 4) != 0:
        print(ray.origin)
        print(ray.dir)
        raise ValueError("Intersection error!")

    n1 = hit.normal
    n2 = bs.shader.get_value('hit.normal')
    if round(n1.x-n2.x, 4) != 0 or round(n1.y-n2.y, 4) != 0 or round(n1.z-n2.z, 4) != 0:
        print(ray.origin)
        print(ray.dir)
        raise ValueError("Intersection error!")


def isect(bbox, shader, linear):
    #origin = Vector3(0.0, 0.0, 0.0)
    origin = random_in_bbox(bbox)
    direction = random_in_bbox(bbox)
    direction.normalize()
    ray = Ray(origin, direction)
    hit = HitPoint()
    props = {'hit': hit, 'ret': 5, 'ray': ray}
    shader.props = props
    shader.update()

    shader.execute()
    h = linear.isect(ray)
    compare(h, shader, ray)
    if h is False:
        return 0
    return 1

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('fname')
    args = parser.parse_args()

    #populate manager with triangles
    mgr = ShapeManager()
    populate_mgr(mgr, args.fname)
    bbox = mgr.bbox()

    linear = LinearIsect(mgr)
    runtime = Runtime()
    shader = linear.isect_shader([runtime])
    hit2 = HitPoint()
    origin = Vector3(0.0, 0.0, 0.0)
    direction = Vector3(1.2, 1.1, 1.12)
    direction.normalize()
    ray = Ray(origin, direction)
    props = {'hit': hit2, 'ret': 0, 'ray': ray}
    code = """
ret = isect(ray, hit)
    """
    bs = BasicShader(code, None, props)
    bs.prepare([runtime], [shader])

    hits = 0
    nrays = 20
    for x in range(nrays):
        hits += isect(bbox, bs, linear)
    print("Fired ray = %s, Number of intersection = %d" % (nrays, hits))

if __name__ == "__main__":
    main()
