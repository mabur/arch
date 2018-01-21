import bpy
import math
from typing import Optional, Sequence, Tuple


Vector3 = Tuple[float, float, float]
Triangle = Tuple[int, int, int]


class Transformation3:
    def transform(self, v: Vector3) -> Vector3:
        raise NotImplementedError()
    def does_mirror(self) -> bool:
        raise NotImplementedError()


class Identity(Transformation3):
    def transform(self, v: Vector3) -> Vector3:
        return v
    def does_mirror(self) -> bool:
        return False

class Composed(Transformation3):
    def __init__(self, outer: Transformation3, inner: Transformation3):
        self.outer = outer
        self.inner = inner
    def transform(self, v: Vector3) -> Vector3:
        return self.outer.transform(self.inner.transform(v))
    def does_mirror(self) -> bool:
        return self.outer.does_mirror() != self.inner.does_mirror()


class SwapXY(Transformation3):
    def transform(self, v: Vector3) -> Vector3:
        return v[1], v[0], v[2]
    def does_mirror(self) -> bool:
        return True


class SwapXZ(Transformation3):
    def transform(self, v: Vector3) -> Vector3:
        return v[2], v[1], v[0]
    def does_mirror(self) -> bool:
        return True


class SwapYZ(Transformation3):
    def transform(self, v: Vector3) -> Vector3:
        return v[0], v[2], v[1]
    def does_mirror(self) -> bool:
        return True


def clear_scene() -> None:
    objects = bpy.context.scene.objects
    for object in objects:
        objects.unlink(object)
    for data in (bpy.data.objects, bpy.data.meshes, bpy.data.lamps, bpy.data.cameras):
        for data_id in data:
            data.remove(data_id)


def make_mesh(vertices: Sequence[Vector3], faces: Sequence[Tuple], name: str)\
        -> None:
    mesh_data = bpy.data.meshes.new('')
    mesh_data.from_pydata(vertices, [], faces)
    mesh_data.update()
    return mesh_data


def make_object(mesh, name: str) -> None:
    obj = bpy.data.objects.new('', mesh)
    bpy.context.scene.objects.link(obj)


def make_mesh_object(vertices: Sequence[Vector3],
                     triangles: Sequence[Triangle],
                     transformation: Optional[Transformation3] = None) -> None:
    transformed_vertices = vertices if not transformation else\
        [transformation.transform(v) for v in vertices]

    transformed_triangles = triangles if not transformation or not transformation.does_mirror() else\
        [(a, c, b) for a, b, c in triangles]

    mesh = bpy.data.meshes.new('')
    mesh.from_pydata(transformed_vertices, [], transformed_triangles)
    mesh.update()
    obj = bpy.data.objects.new('', mesh)
    bpy.context.scene.objects.link(obj)


def make_triangle(a: Vector3,
                  b: Vector3,
                  c: Vector3,
                  transformation: Optional[Transformation3]=None,
                  name: str='triangle') -> None:
    vertices = [a, b, c]
    faces = [(0, 1, 2)]
    make_mesh_object(vertices=vertices, triangles=faces, transformation=transformation)


def make_rectangle(upper_left: Vector3,
                   upper_right: Vector3,
                   lower_left: Vector3,
                   lower_right: Vector3,
                   transformation: Optional[Transformation3] = None,
                   name: str='rectangle') -> None:
    vertices = [upper_left, upper_right, lower_left, lower_right]
    faces = [(0, 2, 3), (0, 3, 1)]
    make_mesh_object(vertices=vertices, triangles=faces, transformation=transformation)


def make_plane_x_pos(name, zmin, zmax, ymin, ymax, x,
                     transformation: Optional[Transformation3]=None):
    make_rectangle(
        upper_right=(x, ymax, zmin),
        upper_left=(x, ymax, zmax),
        lower_right=(x, ymin, zmin),
        lower_left=(x, ymin, zmax),
        transformation=transformation,
        name=name)


def make_plane_x_neg(name, zmin, zmax, ymin, ymax, x,
                     transformation: Optional[Transformation3]=None):
    make_rectangle(
        upper_left=(x, ymax, zmin),
        upper_right=(x, ymax, zmax),
        lower_left=(x, ymin, zmin),
        lower_right=(x, ymin, zmax),
        transformation=transformation,
        name=name)


def make_plane_y_pos(name, zmin, zmax, xmin, xmax, y,
                     transformation: Optional[Transformation3] = None):
    make_rectangle(
        upper_left=(xmax, y, zmin),
        upper_right=(xmax, y, zmax),
        lower_left=(xmin, y, zmin),
        lower_right=(xmin, y, zmax),
        transformation=transformation,
        name=name)


def make_plane_y_neg(name, zmin, zmax, xmin, xmax, y,
                     transformation: Optional[Transformation3] = None):
    make_rectangle(
        upper_right=(xmax, y, zmin),
        upper_left=(xmax, y, zmax),
        lower_right=(xmin, y, zmin),
        lower_left=(xmin, y, zmax),
        transformation=transformation,
        name=name)


def make_plane_z_pos(name, xmin, xmax, ymin, ymax, z,
                     transformation: Optional[Transformation3] = None):
    make_rectangle(
        upper_left=(xmin, ymax, z),
        upper_right=(xmax, ymax, z),
        lower_left=(xmin, ymin, z),
        lower_right=(xmax, ymin, z),
        transformation=transformation,
        name=name)


def make_plane_z_neg(name, xmin, xmax, ymin, ymax, z,
                     transformation: Optional[Transformation3] = None):
    make_rectangle(
        upper_right=(xmin, ymax, z),
        upper_left=(xmax, ymax, z),
        lower_right=(xmin, ymin, z),
        lower_left=(xmax, ymin, z),
        transformation=transformation,
        name=name)


def make_box(xmin: float, xmax: float,
             ymin: float, ymax: float,
             zmin: float, zmax: float,
             transformation: Optional[Transformation3] = None,
             name: str='box') -> None:
    make_plane_x_pos(zmin=zmin, zmax=zmax, ymin=ymin, ymax=ymax, x=xmax, name=name, transformation=transformation)
    make_plane_x_neg(zmin=zmin, zmax=zmax, ymin=ymin, ymax=ymax, x=xmin, name=name, transformation=transformation)

    make_plane_y_pos(zmin=zmin, zmax=zmax, xmin=xmin, xmax=xmax, y=ymax, name=name, transformation=transformation)
    make_plane_y_neg(zmin=zmin, zmax=zmax, xmin=xmin, xmax=xmax, y=ymin, name=name, transformation=transformation)

    make_plane_z_pos(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, z=zmax, name=name, transformation=transformation)
    make_plane_z_neg(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, z=zmin, name=name, transformation=transformation)


def make_arch_y(xmin: float, xmax: float,
                ymin: float, ymax: float,
                zmin: float, zmax: float,
                transformation: Optional[Transformation3] = None,
                name: str='arch') -> None:
    make_plane_y_pos(name=name, zmin=zmin, zmax=zmax, xmin=xmin, xmax=xmax, y=ymax, transformation=transformation)
    make_plane_y_neg(name=name, zmin=zmin, zmax=zmax, xmin=xmin, xmax=xmax, y=ymin, transformation=transformation)
    make_plane_z_pos(name=name, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, z=zmax, transformation=transformation)
    
    STEPS = 32
    angles = [math.pi * i / 2 / (STEPS - 1) for i in range(STEPS)]

    cy = (ymax + ymin) / 2    
    ry = (ymax - ymin) / 2
    rz = zmax - zmin

    def get_y_left(angle):
        return cy + ry * math.cos(angle)
    
    def get_y_right(angle):
        return cy - ry * math.cos(angle)
    
    def get_z(angle):
        return zmin + rz * math.sin(angle)

    def get_front_left(angle):
        return (xmax, get_y_left(angle), get_z(angle))

    def get_front_right(angle):
        return (xmax, get_y_right(angle), get_z(angle))

    def get_back_left(angle):
        return (xmin, get_y_left(angle), get_z(angle))

    def get_back_right(angle):
        return (xmin, get_y_right(angle), get_z(angle))

    vertices_front_left = [get_front_left(angle) for angle in angles]
    vertices_front_right = [get_front_right(angle) for angle in angles]
    vertices_back_left = [get_back_left(angle) for angle in angles]
    vertices_back_right = [get_back_right(angle) for angle in angles]

    corner_back_left = (xmin, ymax, zmax)
    corner_front_left = (xmax, ymax, zmax)
    corner_back_right = (xmin, ymin, zmax)
    corner_front_right = (xmax, ymin, zmax)

    vertices_back_left.append(corner_back_left)
    vertices_back_right.append(corner_back_right)
    vertices_front_left.append(corner_front_left)
    vertices_front_right.append(corner_front_right)

    for step in range(STEPS - 1):
        make_triangle(a=vertices_front_left[step],
                      c=vertices_back_left[step],
                      b=vertices_front_left[step + 1],
                      transformation=transformation)

        make_triangle(a=vertices_back_left[step],
                      c=vertices_back_left[step + 1],
                      b=vertices_front_left[step + 1],
                      transformation=transformation)

        make_triangle(a=vertices_front_right[step],
                      b=vertices_back_right[step],
                      c=vertices_front_right[step + 1],
                      transformation=transformation)

        make_triangle(a=vertices_back_right[step],
                      b=vertices_back_right[step + 1],
                      c=vertices_front_right[step + 1],
                      transformation=transformation)

        make_triangle(a=vertices_back_left[-1],
                      b=vertices_back_left[step],
                      c=vertices_back_left[step + 1],
                      transformation=transformation)

        make_triangle(a=vertices_front_left[-1],
                      c=vertices_front_left[step],
                      b=vertices_front_left[step + 1],
                      transformation=transformation)

        make_triangle(a=vertices_back_right[-1],
                      c=vertices_back_right[step],
                      b=vertices_back_right[step + 1],
                      transformation=transformation)

        make_triangle(a=vertices_front_right[-1],
                      b=vertices_front_right[step],
                      c=vertices_front_right[step + 1],
                      transformation=transformation)


def make_arches_y(num_arches: int, radius: float, height_bottom: float,
                  height_top: float, width_pillar: float,
                  xmin: float, xmax: float, zmin: float,
                  transformation: Optional[Transformation3] = None) -> None:
    diameter = 2 * radius
    height = height_bottom + radius + height_top
    width_segment = diameter + width_pillar

    make_box(
        xmin=xmin, xmax=xmax,
        ymin=0, ymax=width_pillar,
        zmin=zmin, zmax=zmin + height,
        transformation=transformation)

    for i in range(num_arches):
        y = i * width_segment
        make_box(
            xmin=xmin, xmax=xmax,
            ymin=width_segment + y, ymax=width_segment + width_pillar + y,
            zmin=zmin, zmax=zmin + height,
            transformation=transformation)
        make_box(
            xmin=xmin, xmax=xmax,
            ymin=width_pillar + y, ymax=width_segment + y,
            zmin=zmin + height_bottom + radius, zmax=zmin + height,
            transformation=transformation)
        make_arch_y(
            xmin=xmin, xmax=xmax,
            ymin=width_pillar + y, ymax=width_segment + y,
            zmin=zmin + height_bottom, zmax=zmin + height_bottom + radius,
            transformation=transformation)


def make_arches_x(num_arches: int, radius: float, height_bottom: float,
                  height_top: float, width_pillar: float,
                  ymin: float, ymax: float, zmin: float,
                  transformation: Optional[Transformation3] = None) -> None:
    new_transformation = Composed(transformation, SwapXY()) if transformation \
        else SwapXY()

    make_arches_y(
        num_arches=num_arches,
        radius=radius,
        height_bottom=height_bottom,
        height_top=height_top,
        width_pillar=width_pillar,
        xmin=ymin,
        xmax=ymax,
        zmin=zmin,
        transformation=new_transformation)


def main() -> None:
    clear_scene()
    for floor in range(1):
        height = 4
        make_arches_x(num_arches=3, radius=1, height_bottom=2, height_top=1,
            width_pillar=1, ymin=0, ymax=1, zmin=floor * height)
        make_arches_x(num_arches=3, radius=1, height_bottom=2, height_top=1,
            width_pillar=1, ymin=9, ymax=10, zmin=floor * height)
        make_arches_y(num_arches=3, radius=1, height_bottom=2, height_top=1,
            width_pillar=1, xmin=0, xmax=1, zmin=floor * height)
        make_arches_y(num_arches=3, radius=1, height_bottom=2, height_top=1,
            width_pillar=1, xmin=9, xmax=10, zmin=floor * height)
