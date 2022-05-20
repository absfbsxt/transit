from pickle import TRUE
import bpy
import math
import random
from mathutils import Vector
from gpu_extras.batch import batch_for_shader
import shapely.geometry

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

        # Visualization
        # bpy.ops.object.mode_set(mode = 'EDIT')

        # # draw with GPU Module
        # coords = [(v[0], v[1], v[2]) for v in obb_world]

        # indices = (
        #     (0, 1), (1, 2), (2, 3), (3, 0),
        #     (4, 5), (5, 6), (6, 7), (7, 4),
        #     (0, 4), (1, 5), (2, 6), (3, 7))

        # shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        # batch = batch_for_shader(shader, 'LINES', {"pos": coords}, indices=indices)


        # def draw():
        #     shader.bind()
        #     shader.uniform_float("color", (1, 0, 0, 1))
        #     batch.draw(shader)

        # bpy.types.SpaceView3D.draw_handler_add(draw, (), 'WINDOW', 'POST_VIEW')

        object["bottom_poly"] = [obb_world[0][0:2], obb_world[3][0:2], obb_world[4][0:2], obb_world[7][0:2]]
        object["accessArea"] = *

    # box = object.bound_box
    # p = [object.matrix_world @ Vector(corner) for corner in box]

def CheckIfHit(object_1, object_2):
    """
    Description:
    check if object_1's bottom hit to object_2's bottom

    Return:
    True or False
    """
    temp_1 = object_1["bottom_poly"]
    temp_2 = object_2["bottom_poly"]

    obj_1_poly_context = {'type': 'MULTIPOLYGON',
    'coordinates': [[[list(temp_1[0]), list(temp_1[1]), list(temp_1[2]), list(temp_1[3])]]]}
    obj_2_poly_context = {'type': 'MULTIPOLYGON',
    'coordinates': [[[list(temp_2[0]), list(temp_2[1]), list(temp_2[2]), list(temp_2[3])]]]}

    obj_1_poly_shape = shapely.geometry.asShape(obj_1_poly_context)
    obj_2_poly_shape = shapely.geometry.asShape(obj_2_poly_context)
    return obj_1_poly_shape.intersects(obj_2_poly_shape)

def CheckIntersect(object_1, object_2):
    """
    Description:
    check if object_1's bottom in object_2's accessible area and return intersected point list

    Return:
    list of object_1's bottom points which intersected with object_2's access area
    """

    temp = object_2["accessArea"]
    obj_2_poly_context = {'type': 'MULTIPOLYGON',
    'coordinates': [[[list(temp[0]), list(temp[1]), list(temp[2]), list(temp[3])]]]}
    obj_2_poly_shape = shapely.geometry.asShape(obj_2_poly_context)

    intersectPoint = []

    for i in object_1["bottom_poly"]:
        i = shapely.geometry.Point(list(i))
        if obj_2_poly_shape.intersects(i):
            intersectPoint.append(i)
        
    if not list:
        return False
    elif list:
        return intersectPoint
    
def select_from_collection(some_collection):
    """ Recursively select objects from the specified collection """

    list = []
    for a_collection in some_collection.children:
        select_from_collection(a_collection)
    for obj in some_collection.objects:
        obj.select_set(True)
        list.append(obj)

    return list

def calc1(list, object_2):
    """
    Description:
    Calculate the cost when A in B's access area but not hit with B

    list:list of points in access area
    """
    temp = object_2["bottom_poly"]
    obj_2_poly_context = {'type': 'MULTIPOLYGON',
    'coordinates': [[[list(temp[0]), list(temp[1]), list(temp[2]), list(temp[3])]]]}
    obj_2_poly_shape = shapely.geometry.asShape(obj_2_poly_context)
    for i in list:
        i = shapely.geometry.Point(list(i))
        dis = obj_2_poly_shape.distance(i)

def calc2():
    """
    Description:
    Calculate the cost when A in B's access area and hit with B

    """

def costFunction(group):
    list = select_from_collection(group)
    for i in len(list):
        for j in len(list)-i:
            if i-1 != i-1+j:
                # if A in B's access area:
                if CheckIntersect(list[i-1], list[i-1+j]) != False:
                    # if A not hit or cover B
                    if CheckIfHit(list[i-1], list[i-1+j]) == False:
                        Intersect_point_list = CheckIntersect(list[i-1], list[i-1+j])
                        cost = calc1
                    # if A hit or cover B
                    else:
                        cost = calc2
                else:
                    continue
    
    return cost
        
    

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