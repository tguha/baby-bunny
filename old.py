from typing import Tuple
from math import ceil, floor, sqrt, atan2, sin


# Like class Point, but represents vertex in 3d space
class Vertex:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    # Debugging / formats obj
    def __repr__(self) -> str:
        return f"< {self.x}, {self.y}, {self.z} >"


class Fragment:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


# Triangle pulls from class Vertex to create Triangle
class Triangle:
    def __init__(self, a: Vertex, b: Vertex, c: Vertex):
        self.a = a
        self.b = b
        self.c = c

    def __repr__(self) -> str:
        return f"({self.a}, {self.b}, {self.c})"


# make background color a polar coordinate using r, theta to make spiral shape, convert from x y pair to RGB triplet
# change background_color to something else so the line doesn't show up?
def background_color(x: int, y: int) -> list[int]:
    r = sqrt((x - 500) ** 2 + (y - 500) ** 2) / 3
    theta = ((atan2(y - 500, x - 600) + 3.14)/sin(6.28)) * 255
    return [int(r), 0, int(theta) % 256]


# Main method reads obj
def main():
    triangles = read_obj("bunny.obj")
    # Creates 1000 x 1000 grid of pixels
    pixels = [[background_color(x, y) for x in range(1000)] for y in range(1000)]

    # Draws a triangle
    for tri in triangles:
        # Rounding done by floor & ceil, finds min and max values in range 1000
        min_x = floor(max(min(tri.a.x, tri.b.x, tri.c.x), 0))
        max_x = ceil(min(max(tri.a.x, tri.b.x, tri.c.x), 1000))
        min_y = floor(max(min(tri.a.y, tri.b.y, tri.c.y), 0))
        max_y = ceil(min(max(tri.a.y, tri.b.y, tri.c.y), 1000))
        # Loops through x and y, assigns colors to pixels from index 1 in tri
        for y in range(min_y, max_y):
            for x in range(min_x, max_x):
                p = Vertex(x, y, 0)
                if inside_triangle(p, tri.a, tri.b, tri.c):
                    pixels[y][x][1] = 255

    write_bmp(pixels)


# Orient function used to test position of vertices
def orient(a: Vertex, b: Vertex, c: Vertex):
    ab = Vertex(b.x - a.x, b.y - a.y, 0)
    ac = Vertex(c.x - a.x, c.y - a.y, 0)
    cross_product = ab.x * ac.y - ab.y * ac.x

    if cross_product > 0:
        return 1

    else:
        return -1


# Checks whether point is inside triangle or not
def inside_triangle(p: Vertex, a: Vertex, b: Vertex, c: Vertex):
    turns = orient(a, b, p) + orient(b, c, p) + orient(c, a, p)
    return abs(turns) == 3


# Stores indices and vertices of bunny bmp file in list
def read_obj(obj: str) -> list[Triangle]:
    lines = open(obj).readlines()

    indices: list[Tuple[int, int, int]] = []
    vertices: list[Vertex] = []

    for line in lines:
        if line.startswith("f"):
            # Splits list into separate values
            f_value = line.split()
            # Appends values a, b, and c to indices. Subtracts 1 to offset the index not matching on f
            a = int(f_value[1]) - 1
            b = int(f_value[2]) - 1
            c = int(f_value[3]) - 1
            indices.append((a, b, c))

        # Appends values x, y, and z to vertices. Scaled to fit by multiplying values
        elif line.startswith("v"):
            v_value = line.split()
            x = (float(v_value[1]) + 0.12) * 5000
            y = float(v_value[2]) * 5000
            z = float(v_value[3]) * 5000
            vertex = Vertex(x, y, z)
            vertices.append(vertex)

    triangles = [Triangle(vertices[a], vertices[b], vertices[c]) for (a, b, c) in indices]
    return triangles


# Copies header from bmp files, opens and writes bytes
def write_bmp(pixels):
    header = b'BM\xf6\xc6-\x00\x00\x00\x00\x006\x00\x00\x00(\x00\x00\x00\xe8\x03\x00\x00\xe8\x03\x00\x00\x01\x00\x18\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfd\x1f\x00\x00\xfd\x1f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    g = open("old_bunny.bmp", "wb")
    g.write(header)

    for line in pixels:
        for color in line:
            g.write(bytes(color))


if __name__ == '__main__':
    main()
