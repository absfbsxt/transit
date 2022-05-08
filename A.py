from pickle import TRUE
import bpy
import math
import random
from mathutils import Vector
from gpu_extras.batch import batch_for_shader

bpy.context.object.name
bpy.context.scene.transform_orientation_slots[2].type = 'LOCAL'

bpy.context.object["object_front_name"] = bpy.data.object.name.split("_")[0]
bpy.context.object["object_last_name"] = bpy.data.object.name.split("_")[1]

import numpy as np
def ret_obb(verts):
    points = np.asarray(verts)
    means = np.mean(points, axis=1)

    cov = np.cov(points, y = None,rowvar = 0,bias = 1)

    v, vect = np.linalg.eig(cov)

    tvect = np.transpose(vect)
    points_r = np.dot(points, np.linalg.inv(tvect))

    co_min = np.min(points_r, axis=0)
    co_max = np.max(points_r, axis=0)

    xmin, xmax = co_min[0], co_max[0]
    ymin, ymax = co_min[1], co_max[1]
    zmin, zmax = co_min[2], co_max[2]

    xdif = (xmax - xmin) * 0.5
    ydif = (ymax - ymin) * 0.5
    zdif = (zmax - zmin) * 0.5

    cx = xmin + xdif
    cy = ymin + ydif
    cz = zmin + zdif

    corners = np.array([
        [cx - xdif, cy - ydif, cz - zdif],
        [cx - xdif, cy + ydif, cz - zdif],
        [cx + xdif, cy + ydif, cz - zdif],
        [cx + xdif, cy - ydif, cz - zdif],
        [cx - xdif, cy - ydif, cz + zdif],
        [cx - xdif, cy + ydif, cz + zdif],
        [cx + xdif, cy + ydif, cz + zdif],
        [cx + xdif, cy - ydif, cz + zdif],
    ])

    corners = np.dot(corners, tvect)

    return [Vector((el[0], el[1], el[2])) for el in corners]

def Align():
    '''
    Description:
    choose all objects in nected collecction then alined
    '''
    for object in bpy.data.collections["furniture"].all_objects:
        object.select_set(True)
        bpy.ops.transform.transform(mode='ALIGN', value=(0, 0, 0, 0), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
        object.location.z = 0


def properties(object):
    for object in bpy.data.collections["furniture"].all_objects:
        object.orient_vector = object.matrix_local[0:3][0][0:3][:]
    object_front_name = object.name.split("_")[0]
    object_last_name = object.name.split("_")[1]
    
    if object_last_name == 'TV':
        object.front_view 

def touchable(object):
    if object.name.split("_")[0] == 'sofa' or 'table' or 'chair':
        return True
    
    elif object.name.split("_")[0] == 'potting' or 'water_cooler' or 'cupboard':
        return False

def acessableArea(object):
    '''
    Description:

    '''
    for object in bpy.data.collections["furniture"].all_objects:
        object.select_set(True)
        bpy.ops.object.mode_set(mode = 'OBJECT')
        verts = [v.co for v in object.data.vertices]
        obb_local = ret_obb(verts)
        mat = object.matrix_world
        obb_world = [mat @ v for v in obb_local]

        bpy.ops.object.mode_set(mode = 'EDIT')

        # draw with GPU Module
        coords = [(v[0], v[1], v[2]) for v in obb_world]

        indices = (
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7))

        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'LINES', {"pos": coords}, indices=indices)


        def draw():
            shader.bind()
            shader.uniform_float("color", (1, 0, 0, 1))
            batch.draw(shader)

        bpy.types.SpaceView3D.draw_handler_add(draw, (), 'WINDOW', 'POST_VIEW')

        bottom_poly = 

    # box = object.bound_box
    # p = [object.matrix_world @ Vector(corner) for corner in box]



def simulated_annealing(group_obj):
    """
    """
    #         roomPoints= [geometry.Point(0,0),geometry.Point(100,0)
    #                      ,geometry.Point(100,100),geometry.Point(0,100)]

    # num: iteration times
    # alpha: cooling index
    T_0 = 100
    T_F = 0.1
    num = 250
    count = 0
    alpha = 0.99
    T = T_0
    global beta
    beta = -1/T    
    # initial arrangement
    c_0 = initial

    T = T_0
    while T > T_F:
        for i in range(num):
            # for idx in enumerate(self.redAreas):
            #     self.move()
            
            c_0 = 1
            new_c = 2
            if i == 0:
                old_c = c_0
            if Metropolis(old_c, new_c):
                old_c = new_c
                T = T * alpha
                count += 1
            

def Metropolis(old_c, new_c):
    """
    Description:
    

    """
    if new_c < old_c:
        
        return 1
    else:
        probability = math.exp(beta*(old_c - new_c))

        # recieve new solution probably
        if random() < probability:
            return 1
        else:
            return 0   