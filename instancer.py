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
        selected = context.selected_objects
        groups = {}     # list with groups of objct and its instances {obj2: [obj5, obj3], obj4: [obj1], ...}
        for obj in selected:
            bases = groups.keys()
            for base in bases:
                if __class__.is_instance(obj, base):
                    groups[base].append(obj)
                else:
                    groups[obj] = []




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