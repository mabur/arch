import bpy
import math
import sys


def clear_scene():
    objects = bpy.context.scene.objects
    for object in objects:
        objects.unlink(object)


def make_mesh(name, vertices, faces):
    mesh_data = bpy.data.meshes.new('')
    mesh_data.from_pydata(vertices, [], faces)
    mesh_data.update()
    return mesh_data


def make_object(name, mesh):
    obj = bpy.data.objects.new('', mesh)
    bpy.context.scene.objects.link(obj)


def make_box(xmin, xmax, ymin, ymax, zmin, zmax, name='box'):
    make_plane_x_pos(name=name, zmin=zmin, zmax=zmax, ymin=ymin, ymax=ymax, x=xmax)
    make_plane_x_neg(name=name, zmin=zmin, zmax=zmax, ymin=ymin, ymax=ymax, x=xmin)

    make_plane_y_pos(name=name, zmin=zmin, zmax=zmax, xmin=xmin, xmax=xmax, y=ymax)
    make_plane_y_neg(name=name, zmin=zmin, zmax=zmax, xmin=xmin, xmax=xmax, y=ymin)

    make_plane_z_pos(name=name, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, z=zmax)
    make_plane_z_neg(name=name, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, z=zmin)


def make_plane_x_pos(name, zmin, zmax, ymin, ymax, x):
    make_rectangle(upper_right=(x, ymax, zmin), upper_left=(x, ymax, zmax),
                   lower_right=(x, ymin, zmin), lower_left=(x, ymin, zmax), name=name)


def make_plane_x_neg(name, zmin, zmax, ymin, ymax, x):
    make_rectangle(upper_left=(x, ymax, zmin), upper_right=(x, ymax, zmax),
                   lower_left=(x, ymin, zmin), lower_right=(x, ymin, zmax), name=name)


def make_plane_y_pos(name, zmin, zmax, xmin, xmax, y):
    make_rectangle(upper_left=(xmax, y, zmin), upper_right=(xmax, y, zmax),
                   lower_left=(xmin, y, zmin), lower_right=(xmin, y, zmax), name=name)


def make_plane_y_neg(name, zmin, zmax, xmin, xmax, y):
    make_rectangle(upper_right=(xmax, y, zmin), upper_left=(xmax, y, zmax),
                   lower_right=(xmin, y, zmin), lower_left=(xmin, y, zmax), name=name)


def make_plane_z_pos(name, xmin, xmax, ymin, ymax, z):
    make_rectangle(upper_left=(xmin, ymax, z), upper_right=(xmax, ymax, z),
                   lower_left=(xmin, ymin, z), lower_right=(xmax, ymin, z), name=name)


def make_plane_z_neg(name, xmin, xmax, ymin, ymax, z):
    make_rectangle(upper_right=(xmin, ymax, z), upper_left=(xmax, ymax, z),
                   lower_right=(xmin, ymin, z), lower_left=(xmax, ymin, z), name=name)


def make_rectangle(name, upper_left, upper_right, lower_left, lower_right):
    vertices = [upper_left, upper_right,
                lower_left, lower_right]
    faces = [(0,2,3,1)]
    mesh_name = '{}_mesh'.format(name)
    mesh = make_mesh(name=mesh_name, vertices=vertices, faces=faces)
    make_object(name, mesh)


def make_triangle(name, a, b, c):
    vertices = [a, b, c]
    faces = [(0,1,2)]
    mesh_name = '{}_mesh'.format(name)
    mesh = make_mesh(name=mesh_name, vertices=vertices, faces=faces)
    make_object(name, mesh)


def make_arch_y(xmin, xmax, ymin, ymax, zmin, zmax, name='arch'):
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


def make_arches_y(num_arches, radius, height_bottom, height_top, width_pillar,
        xmin, xmax, zmin):
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


def main():
    clear_scene()
    make_arches_y(num_arches=1, radius=1, height_bottom=3, height_top=1,
        width_pillar=1, xmin=0, xmax=1, zmin=0)
    make_arches_y(num_arches=1, radius=1, height_bottom=3, height_top=1,
        width_pillar=1, xmin=0, xmax=1, zmin=4)