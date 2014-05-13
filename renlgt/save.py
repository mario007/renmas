
import struct
import time
from array import array

import x86
from sdl import memcpy, Vector3
from .buffers import VertexBuffer, VertexNBuffer, VertexUVBuffer,\
    VertexNUVBuffer, TriangleBuffer
from .bbox import BBox
from .grid_mesh import GridMesh

#HEADER 16 - bytes
# magic number 4 bytes
# vbid - 4 bytes
# tbid - 4 bytes
# grid - 4 bytes
#----------------------
## vertex buffer  nbytes|array of bytes
# nitems - 8 bytes
# array of nbytes
#----------------------
## trinagle buffer  nbytes|array of bytes
# nitems - 8 bytes
# array of nbytes
#----------------------
## grid
# bbox - min_p1, max_p2 six doubles(48 bytes)
# dimension  - nx | ny | nz - ints(12 bytes)
# num_objects - int(4 byte)
# num_arrays - int(4 byte) 
# cells - cells of grid
# lin_array - indexes of triangles in cell

def create_buffer(buf_id, nitems):
    ids = {0: VertexBuffer, 1: VertexNBuffer, 2: VertexUVBuffer,
           3: VertexNUVBuffer, 4: TriangleBuffer}
    buf = ids[buf_id](reserve=nitems)
    return buf

def buffer_id(buf):
    if buf is None:
        return -1
    ids = {VertexBuffer: 0, VertexNBuffer: 1, VertexUVBuffer: 2,
           VertexNUVBuffer: 3, TriangleBuffer: 4}
    return ids[type(buf)]


def write_buf_to_file(f, buf):
    f.write(struct.pack('Q', buf.size()))
    buff_size = buf.item_size() * buf.size()
    chunck_size = 50000000  # around 50 MB 
    bytes_read = 0
    while bytes_read < buff_size:
        arr = buf.read_bytes(offset=bytes_read, nbytes=chunck_size)
        bytes_read += len(arr)
        arr.tofile(f)


def read_buf_from_file(f, buf_id):
    nitems = struct.unpack('Q', f.read(8))[0]
    buf = create_buffer(buf_id, nitems)
    nbytes = buf.item_size() * nitems
    arr = array('B')
    arr.fromfile(f, nbytes)

    address = arr.buffer_info()[0]
    memcpy(buf._address.ptr(), address, nbytes) 
    buf._size = nitems
    return buf


def write_grid_to_file(f, grid):
    b = grid.bbox
    bbox = struct.pack('dddddd', b.x0, b.y0, b.z0, b.x1, b.y1, b.z1)
    f.write(bbox)
    dim = struct.pack('iii', grid.nx, grid.ny, grid.nz)
    f.write(dim)
    f.write(struct.pack('I', grid.num_objects))
    f.write(struct.pack('I', grid.num_arrays))

    nbytes = int(grid.nx * grid.ny * grid.nz) * 4

    arr = array('B', [0]*nbytes)
    address = arr.buffer_info()[0]
    memcpy(address, grid.asm_cells.ptr(), nbytes) 
    arr.tofile(f)

    nbytes = grid.num_arrays * 4 + grid.num_objects * 4 + 4
    arr = array('B', [0]*nbytes)
    address = arr.buffer_info()[0]
    memcpy(address, grid.lin_array.ptr(), nbytes) 
    arr.tofile(f)


def read_grid_from_file(f):
    x0, y0, z0, x1, y1, z1 = struct.unpack('dddddd', f.read(48))
    nx, ny, nz = struct.unpack('iii', f.read(12))
    num_objects = struct.unpack('I', f.read(4))[0]
    num_arrays = struct.unpack('I', f.read(4))[0]

    nbytes = nx * ny * nz * 4
    arr = array('B')
    arr.fromfile(f, nbytes)
    address = arr.buffer_info()[0]
    asm_cells = x86.MemData(nbytes)
    memcpy(asm_cells.ptr(), address, nbytes)

    nbytes = num_arrays * 4 + num_objects * 4 + 4
    arr = array('B')
    arr.fromfile(f, nbytes)
    address = arr.buffer_info()[0]
    lin_array = x86.MemData(nbytes)
    memcpy(lin_array.ptr(), address, nbytes)

    bbox = BBox(Vector3(x0, y0, z0), Vector3(x1, y1, z1))
    grid = GridMesh()
    grid.bbox = bbox
    grid.nx = nx
    grid.ny = ny
    grid.nz = nz
    grid.num_objects = num_objects
    grid.num_arrays = num_arrays
    grid.asm_cells = asm_cells
    grid.lin_array = lin_array
    return grid


def save_mesh_data(fname, vb=None, tb=None, grid=None):

    magic_number = 0xACDA
    vbid = buffer_id(vb)
    tbid = buffer_id(tb)
    grid_id = -1 if grid is None else 1
    header = struct.pack('iiii', magic_number, vbid, tbid, grid_id)

    with open(fname, mode='wb') as f:
        f.write(header)
        if vb is not None:
            write_buf_to_file(f, vb)
        if tb is not None:
            write_buf_to_file(f, tb)
        if grid is not None:
            write_grid_to_file(f, grid)


def load_mesh_data(fname):
    vb = tb = grid = None
    with open(fname, mode='rb') as f:
        magic_number, vbid, tbid, grid_id = struct.unpack('iiii', f.read(16))
        if magic_number != 0xACDA:
            raise ValueError("Not valid file format! ", fname)
        if vbid != -1:
            vb = read_buf_from_file(f, vbid)
        if tbid != -1:
            tb = read_buf_from_file(f, tbid)
        if grid_id != -1:
            grid = read_grid_from_file(f)

    return (vb, tb, grid)

