import bpy
import math
import sys
from typing import Callable, Sequence, Tuple

Vector3 = Tuple[float, float, float]
Transformation3 = Callable[[Vector3], Vector3]


def identity(v: Vector3) -> Vector3:
    return v
    #return swap_xy(v)

# TODO: Do I want to support mirroring?
# If so, then could add a parity flag.

def swap_xy(v: Vector3) -> Vector3:
    return (v[1], v[0], v[2])


def swap_xz(v: Vector3) -> Vector3:
    return (v[2], v[1], v[0])


def swap_yz(v: Vector3) -> Vector3:
    return (v[0], v[2], v[1])


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


def make_triangle(a: Vector3,
                  b: Vector3,
                  c: Vector3,
                  transformation: Transformation3=identity,
                  name: str='triangle') -> None:
    vertices = [transformation(a), transformation(b), transformation(c)]
    faces = [(0, 1, 2)]
    name_mesh = '{}_mesh'.format(name)
    name_object = '{}_object'.format(name)
    mesh = make_mesh(name=name_mesh, vertices=vertices, faces=faces)
    make_object(name=name_object, mesh=mesh)


def make_rectangle(upper_left: Vector3,
                   upper_right: Vector3,
                   lower_left: Vector3,
                   lower_right: Vector3,
                   transformation: Transformation3=identity,
                   name: str='rectangle') -> None:
    vertices = [transformation(upper_left), transformation(upper_right),
                transformation(lower_left), transformation(lower_right)]
    #faces = [(0, 2, 3, 1)]
    faces = [(0, 2, 3), (0, 3, 1)]
    name_mesh = '{}_mesh'.format(name)
    name_object = '{}_object'.format(name)
    mesh = make_mesh(name=name_mesh, vertices=vertices, faces=faces)
    make_object(name=name_object, mesh=mesh)


def make_plane_x_pos(name, zmin, zmax, ymin, ymax, x, transformation: Transformation3=identity):
    make_rectangle(
        upper_right=(x, ymax, zmin),
        upper_left=(x, ymax, zmax),
        lower_right=(x, ymin, zmin),
        lower_left=(x, ymin, zmax),
        transformation=transformation,
        name=name)


def make_plane_x_neg(name, zmin, zmax, ymin, ymax, x, transformation: Transformation3=identity):
    make_rectangle(
        upper_left=(x, ymax, zmin),
        upper_right=(x, ymax, zmax),
        lower_left=(x, ymin, zmin),
        lower_right=(x, ymin, zmax),
        transformation=transformation,
        name=name)


def make_plane_y_pos(name, zmin, zmax, xmin, xmax, y, transformation: Transformation3=identity):
    make_rectangle(
        upper_left=(xmax, y, zmin),
        upper_right=(xmax, y, zmax),
        lower_left=(xmin, y, zmin),
        lower_right=(xmin, y, zmax),
        transformation=transformation,
        name=name)


def make_plane_y_neg(name, zmin, zmax, xmin, xmax, y, transformation: Transformation3=identity):
    make_rectangle(
        upper_right=(xmax, y, zmin),
        upper_left=(xmax, y, zmax),
        lower_right=(xmin, y, zmin),
        lower_left=(xmin, y, zmax),
        transformation=transformation,
        name=name)


def make_plane_z_pos(name, xmin, xmax, ymin, ymax, z, transformation: Transformation3=identity):
    make_rectangle(
        upper_left=(xmin, ymax, z),
        upper_right=(xmax, ymax, z),
        lower_left=(xmin, ymin, z),
        lower_right=(xmax, ymin, z),
        transformation=transformation,
        name=name)


def make_plane_z_neg(name, xmin, xmax, ymin, ymax, z, transformation: Transformation3=identity):
    make_rectangle(upper_right=(xmin, ymax, z), upper_left=(xmax, ymax, z),
                   lower_right=(xmin, ymin, z), lower_left=(xmax, ymin, z), name=name)


def make_box(xmin: float, xmax: float,
             ymin: float, ymax: float,
             zmin: float, zmax: float,
             transformation: Transformation3=identity,
             name: str='box') -> None:
    make_plane_x_pos(zmin=zmin, zmax=zmax, ymin=ymin, ymax=ymax, x=xmax, name=name)
    make_plane_x_neg(zmin=zmin, zmax=zmax, ymin=ymin, ymax=ymax, x=xmin, name=name)

    make_plane_y_pos(zmin=zmin, zmax=zmax, xmin=xmin, xmax=xmax, y=ymax, name=name)
    make_plane_y_neg(zmin=zmin, zmax=zmax, xmin=xmin, xmax=xmax, y=ymin, name=name)

    make_plane_z_pos(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, z=zmax, name=name)
    make_plane_z_neg(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, z=zmin, name=name)


def make_arch_y(xmin: float, xmax: float,
                ymin: float, ymax: float,
                zmin: float, zmax: float, name: str='arch') -> None:
    make_plane_y_pos(name=name, zmin=zmin, zmax=zmax, xmin=xmin, xmax=xmax, y=ymax)
    make_plane_y_neg(name=name, zmin=zmin, zmax=zmax, xmin=xmin, xmax=xmax, y=ymin)
    make_plane_z_pos(name=name, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, z=zmax)
    
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
    
    for step in range(STEPS - 1):
        a0 = angles[step]
        a1 = angles[step + 1]
        y0l = get_y_left(a0)
        y1l = get_y_left(a1)
        y0r = get_y_right(a0)
        y1r = get_y_right(a1)
        z0 = get_z(a0)
        z1 = get_z(a1)
        make_rectangle(upper_left=(xmin, y0l, z0), upper_right=(xmin, y1l, z1),
                       lower_left=(xmax, y0l, z0), lower_right=(xmax, y1l, z1), name=name)
        make_rectangle(upper_right=(xmin, y0r, z0), upper_left=(xmin, y1r, z1),
                       lower_right=(xmax, y0r, z0), lower_left=(xmax, y1r, z1), name=name)
        make_triangle(name=name, a=(xmin,ymax,zmax), b=(xmin,y0l,z0), c=(xmin,y1l,z1))
        make_triangle(name=name, a=(xmax,ymax,zmax), c=(xmax,y0l,z0), b=(xmax,y1l,z1))
        
        make_triangle(name=name, a=(xmin,ymin,zmax), c=(xmin,y0r,z0), b=(xmin,y1r,z1))
        make_triangle(name=name, a=(xmax,ymin,zmax), b=(xmax,y0r,z0), c=(xmax,y1r,z1))


def make_arches_y(num_arches: int, radius: float, height_bottom: float,
                  height_top: float, width_pillar: float,
                  xmin: float, xmax: float, zmin: float) -> None:
    diameter = 2 * radius
    height = height_bottom + radius + height_top
    width_segment = diameter + width_pillar

    make_box(
        xmin=xmin, xmax=xmax,
        ymin=0, ymax=width_pillar,
        zmin=zmin, zmax=zmin + height)

    for i in range(num_arches):
        y = i * width_segment
        make_box(
            xmin=xmin, xmax=xmax,
            ymin=width_segment + y, ymax=width_segment + width_pillar + y,
            zmin=zmin, zmax=zmin + height)
        make_box(
            xmin=xmin, xmax=xmax,
            ymin=width_pillar + y, ymax=width_segment + y,
            zmin=zmin + height_bottom + radius, zmax=zmin + height)
        make_arch_y(
            xmin=xmin, xmax=xmax,
            ymin=width_pillar + y, ymax=width_segment + y,
            zmin=zmin + height_bottom, zmax=zmin + height_bottom + radius)


def main() -> None:
    clear_scene()
    make_arches_y(num_arches=1, radius=1, height_bottom=3, height_top=1,
        width_pillar=1, xmin=0, xmax=1, zmin=0)
    make_arches_y(num_arches=1, radius=1, height_bottom=3, height_top=1,
        width_pillar=1, xmin=0, xmax=1, zmin=4)
