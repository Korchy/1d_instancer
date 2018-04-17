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
        print('-'*50)
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
                tmprez = __class__.check_level_1(obj1, obj2)
                rez.append(tmprez)
                if not tmprez:
                    print(obj1, obj2, ' - Dont match by Dimenstions')
            # len of data
            if context.window_manager.instancer_vars.level_2:
                tmprez = __class__.check_level_2(obj1, obj2)
                rez.append(tmprez)
                if not tmprez:
                    print(obj1, obj2, ' - Dont match by Length of Data')
            # tris count
            if context.window_manager.instancer_vars.level_3:
                tmprez = __class__.check_level_3(obj1, obj2)
                rez.append(tmprez)
                if not tmprez:
                    print(obj1, obj2, ' - Dont match by Tris count')
            # vertex position with tolerance
            # в tolerance - на сколько могут различаться координаты вертексов
            if context.window_manager.instancer_vars.level_4:
                tmprez = __class__.check_level_4(obj1, obj2, context.window_manager.instancer_vars.tolerance)
                rez.append(tmprez)
                if not tmprez:
                    print(obj1, obj2, ' - Dont match by Vertes position with tolerance')
            # vertex position with round
            # в treshold - порядок округления
            if context.window_manager.instancer_vars.level_5:
                tmprez = __class__.check_level_5(obj1, obj2, context.window_manager.instancer_vars.treshold)
                rez.append(tmprez)
                if not tmprez:
                    print(obj1, obj2, ' - Dont match by Vertes position with round')

            # add here more levels



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
    def check_level_4(obj1, obj2, abs_tol):
        # vertex position with tolerance
        # abs_tol - на сколько могут различаться координаты вертексов
        rez = True
        for vert in obj1.data.vertices:
            # if vert.co != obj2.data.vertices[vert.index].co:
            if not __class__.rounded_vector_comp(vert.co, obj2.data.vertices[vert.index].co, abs_tol):
                rez = False
                break
        return rez

    @staticmethod
    def rounded_vector_comp(v1, v2, abs_tol):
        return math.isclose(v1[0], v2[0], abs_tol=abs_tol) and math.isclose(v1[1], v2[1], abs_tol=abs_tol) and math.isclose(v1[2], v2[2], abs_tol=abs_tol)

    @staticmethod
    def check_level_5(obj1, obj2, treshold):
        # vertex position with log rounding
        rez = True
        # exp = 0 if treshold == 0 else (10**(-len(str(treshold).split('.')[1])) if treshold < 1 else 10**(len(str(treshold).split('.')[0])-1))
        # without round
        if treshold == 0:
            for vert in obj1.data.vertices:
                if vert.co != obj2.data.vertices[vert.index].co:
                    rez = False
                    break
        # round < 1
        elif treshold < 1:
            exp = len(str(treshold).split('.')[1])
            for vert in obj1.data.vertices:
                if round(vert.co[0], exp) != round(obj2.data.vertices[vert.index].co[0], exp)\
                        or round(vert.co[1], exp) != round(obj2.data.vertices[vert.index].co[1], exp)\
                        or round(vert.co[2], exp) != round(obj2.data.vertices[vert.index].co[2], exp):
                    rez = False
                    break
        # round > 1
        else:
            # exp = len(str(treshold).split('.')[0])
            exp = 10**(len(str(treshold).split('.')[0])-1)
            for vert in obj1.data.vertices:
                if int(vert.co[0]/exp)*exp != int(obj2.data.vertices[vert.index].co[0]/exp)*exp\
                        or int(vert.co[1]/exp)*exp != int(obj2.data.vertices[vert.index].co[1]/exp)*exp\
                        or int(vert.co[2]/exp)*exp != int(obj2.data.vertices[vert.index].co[2]/exp)*exp:
                    rez = False
                    break
        return rez


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
        name='Vertex position with tolerance',
        default=True
    )
    tolerance = bpy.props.FloatProperty(
        name='Tolerance',
        subtype='UNSIGNED',
        precision=6,
        min=0.0,
        default=0.0
    )
    level_5 = bpy.props.BoolProperty(
        name='Vertex position with round',
        default=True
    )
    treshold = bpy.props.FloatProperty(
        name='Treshold',
        subtype='UNSIGNED',
        precision=6,
        min=0.0,
        default=0.01
    )


class InstancerPanel(bpy.types.Panel):
    bl_idname = 'instancer.panel'
    bl_label = 'Instancer'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = '1D'

    def draw(self, context):
        self.layout.operator('instancer.search', icon='FULLSCREEN_EXIT', text='Collaps to instances')
        self.layout.prop(context.window_manager.instancer_vars, 'level_1')
        self.layout.prop(context.window_manager.instancer_vars, 'level_2')
        self.layout.prop(context.window_manager.instancer_vars, 'level_3')
        self.layout.prop(context.window_manager.instancer_vars, 'level_4')
        self.layout.prop(context.window_manager.instancer_vars, 'tolerance')
        self.layout.prop(context.window_manager.instancer_vars, 'level_5')
        self.layout.prop(context.window_manager.instancer_vars, 'treshold')


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
