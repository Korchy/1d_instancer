# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#   https://github.com/Korchy/1d_instancer
#
# Version history:
#   1.0. - research


import bpy


class Instancer:

    @staticmethod
    def search_for_instances(context):
        # selected = context.selected_objects
        groups = {}     # list with groups of objects and its instances {obj2: [obj5, obj3], obj4: [obj1], ...}
        active = context.active_object
        groups[active] = []
        search_cloud = [obj for obj in bpy.data.objects if obj.type == 'MESH' and obj != context.active_object]
        for obj in search_cloud:
            bases = list(groups.keys())
            for base in bases:
                if __class__.is_instance(obj, base):
                    groups[base].append(obj)
                else:
                    groups[obj] = []
        print(groups)

    @staticmethod
    def is_instance(obj1, obj2):
        # dimensions
        if not __class__.check_level_1(obj1, obj2):
            return False
        # len of data
        if not __class__.check_level_2(obj1, obj2):
            return False
        # tris count
        if not __class__.check_level_3(obj1, obj2):
            return False
        # vertex position
        if not __class__.check_level_4(obj1, obj2):
            return False
        return True

    @staticmethod
    def check_level_1(obj1, obj2):
        # dimensions
        return obj1.dimensions == obj2.dimensions

    @staticmethod
    def check_level_2(obj1, obj2):
        # vertices, edges, polygons count
        return len(obj1.data.vertices) == len(obj2.data.vertices) and len(obj1.data.polygons) == len(obj2.data.polygons) and len(obj1.data.edges) == len(obj2.data.edges)

    @staticmethod
    def check_level_3(obj1, obj2):
        # tris count
        obj1_tris = 0
        obj2_tris = 0
        for polygon in obj1.data.polygons:
            obj1_tris += len(polygon.vertices) - 2
        for polygon in obj2.data.polygons:
            obj2_tris += len(polygon.vertices) - 2
        return obj1_tris == obj2_tris

    @staticmethod
    def check_level_4(obj1, obj2):
        # vertex position with rounding
        rez = True
        for vert in obj1.data.vertices:
            if vert.co != obj2.data.vertices[vert.index].co:
                rez = False
                break
        return rez

    @staticmethod
    def sample(context):

        # sample from P.K.

        import bpy

        data = bpy.context.active_object.data
        dim = bpy.context.active_object.dimensions
        mat = bpy.context.active_object.matrix_world
        trismain = 0
        for p in bpy.context.active_object.data.polygons:
            trismain += len(p.vertices) - 2
        LV = len(data.vertices)
        LE = len(data.edges)
        LF = len(data.polygons)

        name = []

        for i in bpy.context.visible_objects:
            temp = True
            tris = 0
            if data.name == i.data.name:
                continue
            if i.dimensions[0] == dim[0] and i.dimensions[1] == dim[1] and i.dimensions[2] == dim[2]:
                if len(i.data.vertices) == LV and len(i.data.edges) == LE and len(i.data.polygons) == LF:
                    for p in i.data.polygons:
                        tris += len(p.vertices) - 2
                    if trismain == tris:
                        for j in i.data.vertices:
                            if j.co != data.vertices[j.index].co:
                                temp = False
                                continue
                    if temp:
                        name.append(i.name)

        bpy.ops.object.select_all(action='DESELECT')

        for i in name:
            bpy.data.objects[i].select = True

        bpy.context.active_object.select = True
        bpy.ops.object.make_links_data(type='OBDATA')
        bpy.ops.object.select_linked(type='OBDATA')