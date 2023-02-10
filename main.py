import math
import random
from typing import Tuple, Self, Callable
from math import ceil, floor, sqrt, atan2, sin

# TODO: Use color components of background vertices for background effect
# TODO: screen space should be 0-1, not 0-1000
# TODO: Maybe rescale objects to a standard size (not necessarily good practice)
# TODO: Find other objects to draw with bunny (eyes?)
# TODO: Maybe make vec2, vec3, and vec4 classes
# TODO: use matrix multiplication for "project" function (Model matrix, Camera Matrix)
# TODO: Lighting using vertex normals
# TODO: Transparency?
# TODO: Textures


# Like class Point, but represents vertex in 3d space
# coord in world space
class Vertex:
    def __init__(self, x: float, y: float, z: float, r: float = 0, g: float = 0, b: float = 0):
        self.x = x
        self.y = y
        self.z = z
        self.r = r
        self.g = g
        self.b = b

    def project(self):
        self.x = (self.x + 0.12) * 5000
        self.y = self.y * 5000
        self.z = self.z * 5000

    def get_color(self):
        # {-300,300}->{300,-300}->{0.5,-0.5}->{1,0}
        # (-self.z / 600) + 0.5
        brightness = (self.z / 600) + 0.5

        r = self.r * brightness
        g = self.g * brightness
        b = self.b * brightness

        return [max(min(int(b * 256), 255), 0),
                max(min(int(g * 256), 255), 0),
                max(min(int(r * 256), 255), 0)]

    # make background color a polar coordinate using r, theta to make spiral shape, convert from x y pair to RGB triplet
    # change background_color to something else so the line doesn't show up?
    def background_color(self) -> list[int]:
        r = sqrt((self.x - 500) ** 2 + (self.y - 500) ** 2) / 3
        theta = ((atan2(self.y - 500, self.x - 600) + 3.14) / sin(6.28)) * 255
        return [int(r), 0, int(theta) % 256]

    # Debugging / formats obj
    def __repr__(self) -> str:
        return f"< {self.x}, {self.y}, {self.z} >"

    def __mul__(self, other: float):
        x = self.x * other
        y = self.y * other
        z = self.z * other
        r = self.r * other
        g = self.g * other
        b = self.b * other
        return Vertex(x, y, z, r, g, b)

    def __add__(self, other: Self) -> Self:
        x = self.x + other.x
        y = self.y + other.y
        z = self.z + other.z
        r = self.r + other.r
        g = self.g + other.g
        b = self.b + other.b
        return Vertex(x, y, z, r, g, b)


# Main method reads obj
def main():
    indices, vertices = read_obj("bunny.obj")
    vertices2 = [Vertex(0, 0, -1000, 1, 0, 0),
                 Vertex(1000, 0, -1000, 0, 1, 0),
                 Vertex(0, 1000, -1000, 0, 0, 1),
                 Vertex(1000, 1000, -1000)]
    indices2 = [(0, 1, 2), (2, 1, 3)]

    # Creates 1000 x 1000 grid of pixels
    pixels = [[[0, 0, 0] for _ in range(1000)] for _ in range(1000)]
    depths = [[-math.inf for _ in range(1000)] for _ in range(1000)]
    for vertex in vertices:
        vertex.project()

    # min(vertex.z for vertex in vertices))
    # max(vertex.z for vertex in vertices))
    '''cond = True
    match cond:
        case True:
            return True
        case False:
            return False'''

    render(indices, vertices, depths, pixels, Vertex.get_color)
    render(indices2, vertices2, depths, pixels, Vertex.background_color)
    write_bmp(pixels)


def render(indices: list[Tuple[int, int, int]], vertices: list[Vertex],
           depths: list[list[float]], pixels: list[list[list[float]]],
           shader: Callable[[Vertex], list[int]]):
    for a, b, c in indices:
        a = vertices[a]
        b = vertices[b]
        c = vertices[c]
        # Rounding done by floor & ceil, finds min and max values in range 1000
        min_x = floor(max(min(a.x, b.x, c.x), 0))
        max_x = ceil(min(max(a.x, b.x, c.x), 1000))
        min_y = floor(max(min(a.y, b.y, c.y), 0))
        max_y = ceil(min(max(a.y, b.y, c.y), 1000))
        # Loops through x and y, assigns colors to pixels from index 1 in tri
        for y in range(min_y, max_y):
            for x in range(min_x, max_x):
                vertex = barycentric(x, y, a, b, c)
                if vertex is not None and depths[y][x] < vertex.z:
                    depths[y][x] = vertex.z
                    pixels[y][x] = shader(vertex)


def barycentric(x: float, y: float, a: Vertex, b: Vertex, c: Vertex) -> Vertex | None:
    total = area_triangle(a.x, a.y, b.x, b.y, c.x, c.y)
    a_area = area_triangle(x, y, b.x, b.y, c.x, c.y) / total
    b_area = area_triangle(x, y, c.x, c.y, a.x, a.y) / total
    c_area = area_triangle(a.x, a.y, b.x, b.y, x, y) / total
    if 0 <= a_area <= 1 and 0 <= b_area <= 1 and 0 <= c_area <= 1:
        return (c * c_area) + (b * b_area) + (a * a_area)
    else:
        return None


def area_triangle(x1, y1, x2, y2, x3, y3) -> float:
    return (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)


# Stores indices and vertices of bunny bmp file in list
def read_obj(obj: str) -> Tuple[list[Tuple[int, int, int]], list[Vertex]]:
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
            x = float(v_value[1])
            y = float(v_value[2])
            z = float(v_value[3])
            brightness = random.Random().random() * 0.2 + 0.8
            vertex = Vertex(x, y, z, brightness, brightness, brightness)
            vertices.append(vertex)

    return indices, vertices


# Copies header from bmp files, opens and writes bytes
def write_bmp(pixels):
    header = b'BM\xf6\xc6-\x00\x00\x00\x00\x006\x00\x00\x00(\x00\x00\x00\xe8\x03\x00\x00\xe8\x03\x00\x00\x01\x00\x18\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfd\x1f\x00\x00\xfd\x1f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    g = open("bunny.bmp", "wb")
    g.write(header)

    for line in pixels:
        for color in line:
            g.write(bytes(color))


if __name__ == '__main__':
    main()
