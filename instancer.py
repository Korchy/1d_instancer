# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#   https://github.com/Korchy/1d_instancer
#
# Version history:
#   1.0. - research

bl_info = {
    'name': 'Instancer',
    'category': 'All',
    'author': 'Nikita Akimov',
    'version': (1, 0, 0),
    'blender': (2, 79, 0),
    'location': 'The 3D_View window - T-panel - the 1D tab',
    'wiki_url': 'https://github.com/Korchy/1d_instancer',
    'tracker_url': 'https://github.com/Korchy/1d_instancer',
    'description': 'Instancer - research'
}

import bpy
import math


class Instancer:

    @staticmethod
    def search_for_instances(context):
        groups = {}     # list with groups of objects and its instances {obj2: [obj5, obj3], obj4: [obj1], ...}
        active = context.active_object
        if active:
            groups[active] = []
        # search_cloud = context.selected_objects
        search_cloud = [obj for obj in bpy.data.objects if obj.type == 'MESH' and obj != context.active_object]
        for obj in search_cloud:
            bases = list(groups.keys())
            instance_found = False
            for base in bases:
                if __class__.is_instance(obj, base, context):
                    groups[base].append(obj)
                    instance_found = True
                    break
            if not instance_found:
                groups[obj] = []
        # convert objects in groups to instances
        for group in groups:
            if group == active: # only for active chain now - remove to instance all groups
                bpy.ops.object.select_all(action='DESELECT')
                for obj in groups[group]:
                    obj.select = True
                group.select = True
                context.scene.objects.active = group
                bpy.ops.object.make_links_data(type='OBDATA')
        # select active object group
        bpy.ops.object.select_all(action='DESELECT')
        for obj in groups[active]:
            obj.select = True
        context.scene.objects.active = active
        active.select = True

    @staticmethod
    def is_instance(obj1, obj2, context):
        rez = []
        if obj1 and obj2:
            # dimensions
            if context.window_manager.instancer_vars.level_1:
                rez.append(__class__.check_level_1(obj1, obj2))
            # len of data
            if context.window_manager.instancer_vars.level_2:
                rez.append(__class__.check_level_2(obj1, obj2))
            # tris count
            if context.window_manager.instancer_vars.level_3:
                rez.append(__class__.check_level_3(obj1, obj2))
            # vertex position
            if context.window_manager.instancer_vars.level_4:
                rez.append(__class__.check_level_4(obj1, obj2, context.window_manager.instancer_vars.float_round))
        if rez and False not in rez:
            return True
        else:
            return False

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
        if 'tris' not in obj1:
            obj1_tris = 0
            for polygon in obj1.data.polygons:
                obj1_tris += len(polygon.vertices) - 2
            obj1['tris'] = obj1_tris
        if 'tris' not in obj2:
            obj2_tris = 0
            for polygon in obj2.data.polygons:
                obj2_tris += len(polygon.vertices) - 2
            obj2['tris'] = obj2_tris
        return obj1['tris'] == obj2['tris']

    @staticmethod
    def check_level_4(obj1, obj2, bit):
        # vertex position with rounding
        rez = True
        for vert in obj1.data.vertices:
            # if vert.co != obj2.data.vertices[vert.index].co:
            if not __class__.rounded_vector_comp(vert.co, obj2.data.vertices[vert.index].co, bit):
                rez = False
                break
        return rez

    @staticmethod
    def rounded_vector_comp(v1, v2, bit):
        abs_tol = 1/(10**bit)
        return math.isclose(v1[0], v2[0], abs_tol=abs_tol) and math.isclose(v1[1], v2[1], abs_tol=abs_tol) and math.isclose(v1[2], v2[2], abs_tol=abs_tol)


    @staticmethod
    def sample(context):
        # sample from P.K.
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


class InstancerVars(bpy.types.PropertyGroup):
    float_round = bpy.props.FloatProperty(
        name='FloatRound',
        subtype='UNSIGNED',
        default=0.0
    )
    level_1 = bpy.props.BoolProperty(
        name='Dimensions',
        default=False
    )
    level_2 = bpy.props.BoolProperty(
        name='Len of Data',
        default=True
    )
    level_3 = bpy.props.BoolProperty(
        name='Tris count',
        default=True
    )
    level_4 = bpy.props.BoolProperty(
        name='Vertex position with round',
        default=True
    )


class InstancerPanel(bpy.types.Panel):
    bl_idname = 'instancer.panel'
    bl_label = 'Instancer'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = '1D'

    def draw(self, context):
        self.layout.operator('instancer.search', icon='FULLSCREEN_EXIT', text='Collaps to instances')
        self.layout.prop(context.window_manager.instancer_vars, 'float_round')
        self.layout.prop(context.window_manager.instancer_vars, 'level_1')
        self.layout.prop(context.window_manager.instancer_vars, 'level_2')
        self.layout.prop(context.window_manager.instancer_vars, 'level_3')
        self.layout.prop(context.window_manager.instancer_vars, 'level_4')


class InstancerSearch(bpy.types.Operator):
    bl_idname = 'instancer.search'
    bl_label = 'Search fro instances'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Instancer.search_for_instances(context)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(InstancerSearch)
    bpy.utils.register_class(InstancerVars)
    bpy.utils.register_class(InstancerPanel)
    bpy.types.WindowManager.instancer_vars = bpy.props.PointerProperty(type=InstancerVars)


def unregister():
    del bpy.types.WindowManager.instancer_vars
    bpy.utils.unregister_class(InstancerPanel)
    bpy.utils.unregister_class(InstancerVars)
    bpy.utils.unregister_class(InstancerSearch)


if __name__ == '__main__':
    register()
