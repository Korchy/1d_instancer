# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#   https://github.com/Korchy/1d_instancer
#
# Version history:
#   1.0. - research
#   2018.04.17 (1.0.1) - bugfix - проверка соответстия кол-ва точке в check_level_4 и check_level_5
#   2018.04.17 (1.0.2) - improve - строки 48-49. Если закоментированы - обработка только выделенного меша, если нет - обработка всех мешей по всей сцене
#   2018.04.23 (1.0.3) - improve - whole scene - на галочку
#   2018.04.24 (1.0.4) - improve - select all instance chains, show report, check levels - to continious chain, sliders default value = 0.02,
#   2018.04.24 (1.0.5) - improve - level 6 - check equal materials on each polygons
#   2018.04.25 (1.0.6) - change - level 6 - check material slots (Data and Object)
#   2018.04.29 (1.0.7) - bugfix - check Len of Data anyway in level_6 to prevent errors if not match polygons count


bl_info = {
    'name': 'Instancer',
    'category': 'All',
    'author': 'Nikita Akimov',
    'version': (1, 0, 6),
    'blender': (2, 79, 0),
    'location': 'The 3D_View window - T-panel - the 1D tab',
    'wiki_url': 'https://github.com/Korchy/1d_instancer',
    'tracker_url': 'https://github.com/Korchy/1d_instancer',
    'description': 'Instancer - research'
}

import bpy
import math


class Instancer:

    __textblock_name = 'instances_founded.txt'

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
            if context.window_manager.instancer_vars.whole_scene:
                if not instance_found:
                    groups[obj] = []
        # convert objects in groups to instances
        for group in groups:
            bpy.ops.object.select_all(action='DESELECT')
            for obj in groups[group]:
                obj.select = True
            group.select = True
            context.scene.objects.active = group
            bpy.ops.object.make_links_data(type='OBDATA')
        # select all instance chains
        bpy.ops.object.select_all(action='DESELECT')
        for group in groups.items():
            if group[1]:
                group[0].select = True
                for mesh in group[1]:
                    mesh.select = True
        # show report
        __class__.show_report(context, groups)

    @staticmethod
    def is_instance(obj1, obj2, context):
        rez = True
        if obj1 and obj2:
            # dimensions
            if rez and context.window_manager.instancer_vars.level_1:
                rez = rez and __class__.check_level_1(obj1, obj2)
            # len of data
            if rez and context.window_manager.instancer_vars.level_2:
                rez = rez and __class__.check_level_2(obj1, obj2)
            # tris count
            if rez and context.window_manager.instancer_vars.level_3:
                rez = rez and __class__.check_level_3(obj1, obj2)
            # vertex position with tolerance
            # в tolerance - на сколько могут различаться координаты вертексов
            if rez and context.window_manager.instancer_vars.level_4:
                rez = rez and __class__.check_level_4(obj1, obj2, context.window_manager.instancer_vars.tolerance)
            # vertex position with round
            # в treshold - порядок округления
            if rez and context.window_manager.instancer_vars.level_5:
                rez = rez and __class__.check_level_5(obj1, obj2, context.window_manager.instancer_vars.treshold)
            # materials on polygons
            if rez and context.window_manager.instancer_vars.level_6:
                rez = rez and __class__.check_level_6(obj1, obj2)
            # add here more levels

        return rez

    @staticmethod
    def check_level_1(obj1, obj2):
        # dimensions
        rez = obj1.dimensions == obj2.dimensions
        if not rez:
            print(obj1, obj2, ' - Dont match by Dimenstions')
        return rez

    @staticmethod
    def check_level_2(obj1, obj2):
        # vertices, edges, polygons count
        rez = len(obj1.data.vertices) == len(obj2.data.vertices) and len(obj1.data.polygons) == len(obj2.data.polygons) and len(obj1.data.edges) == len(obj2.data.edges)
        if not rez:
            print(obj1, obj2, ' - Dont match by Length of Data')
        return rez

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
        rez = obj1['tris'] == obj2['tris']
        if not rez:
            print(obj1, obj2, ' - Dont match by Tris count')
        return rez

    @staticmethod
    def check_level_4(obj1, obj2, abs_tol):
        # vertex position with tolerance
        # abs_tol - на сколько могут различаться координаты вертексов
        rez = True
        if not __class__.check_level_2(obj1, obj2):     # check Len of data to prevent errors
            rez = False
        else:
            for vert in obj1.data.vertices:
                # if vert.co != obj2.data.vertices[vert.index].co:
                if not __class__.rounded_vector_comp(vert.co, obj2.data.vertices[vert.index].co, abs_tol):
                    rez = False
                    break
        if not rez:
            print(obj1, obj2, ' - Dont match by Vertes position with tolerance')
        return rez

    @staticmethod
    def rounded_vector_comp(v1, v2, abs_tol):
        return math.isclose(v1[0], v2[0], abs_tol=abs_tol) and math.isclose(v1[1], v2[1], abs_tol=abs_tol) and math.isclose(v1[2], v2[2], abs_tol=abs_tol)

    @staticmethod
    def check_level_5(obj1, obj2, treshold):
        # vertex position with log rounding
        rez = True
        if not __class__.check_level_2(obj1, obj2):     # check Len of data to prevent errors
            rez = False
        else:
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
        if not rez:
            print(obj1, obj2, ' - Dont match by Vertex position with round')
        return rez

    @staticmethod
    def check_level_6(obj1, obj2):
        # Materials on polygons
        rez = True
        if not __class__.check_level_2(obj1, obj2):     # check Len of data to prevent errors
            rez = False
        elif obj1.data.materials and not obj2.data.materials or not obj1.data.materials and obj2.data.materials:
            rez = False
        elif len(obj1.material_slots) == 1 and len(obj2.material_slots) == 1 and obj1.material_slots[0].material != obj2.material_slots[0].material:
            rez = False
        # material indexes on polygons
        elif obj1.data.materials and obj2.data.materials:
            for polygon in obj1.data.polygons:
                polygon1_material_index = polygon.material_index
                polygon2_material_index = obj2.data.polygons[polygon.index].material_index
                if obj1.material_slots[polygon1_material_index].link != obj2.material_slots[polygon2_material_index].link:
                    rez = False
                    break
                if obj1.material_slots[polygon1_material_index].material != obj2.material_slots[polygon2_material_index].material:
                    rez = False
                    break
        if not rez:
            print(obj1, obj2, ' - Dont match by Materials on polygons')
        return rez

    @staticmethod
    def show_report(context, result_list):
        # count
        total_instances = 0
        total_objects = 0
        for group in result_list.items():
            if group[1]:
                total_instances += 1
                total_objects += len(group[1]) + 1
        # show
        textblock = None
        if __class__.__textblock_name in bpy.data.texts:
            textblock = bpy.data.texts[__class__.__textblock_name]
        else:
            textblock = bpy.data.texts.new(name=__class__.__textblock_name)
            textblock.name = __class__.__textblock_name
        textblock.from_string('Linked: {} instances / {} objects'.format(total_instances, total_objects))
        if textblock:
            areatoshow = None
            for area in context.screen.areas:
                if area.type == 'TEXT_EDITOR':
                    areatoshow = area
            if not areatoshow:
                for area in context.screen.areas:
                    if area.type not in ['PROPERTIES', 'INFO', 'OUTLINER', 'VIEW_3D']:
                        areatoshow = area
                        break
            if areatoshow:
                areatoshow.type = 'TEXT_EDITOR'
                areatoshow.spaces.active.text = textblock
                textblock.current_line_index = 0

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
    whole_scene = bpy.props.BoolProperty(
        name='Whole scene',
        default=False
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
        name='Vertex position with tolerance',
        default=True
    )
    tolerance = bpy.props.FloatProperty(
        name='Tolerance',
        subtype='UNSIGNED',
        precision=6,
        min=0.0,
        default=0.02
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
        default=0.02
    )
    level_6 = bpy.props.BoolProperty(
        name='Materials',
        default=True
    )


class InstancerPanel(bpy.types.Panel):
    bl_idname = 'instancer.panel'
    bl_label = 'Instancer'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = '1D'

    def draw(self, context):
        self.layout.prop(context.window_manager.instancer_vars, 'whole_scene')
        self.layout.operator('instancer.search', icon='FULLSCREEN_EXIT', text='Collaps to instances')
        self.layout.prop(context.window_manager.instancer_vars, 'level_1')
        self.layout.prop(context.window_manager.instancer_vars, 'level_2')
        self.layout.prop(context.window_manager.instancer_vars, 'level_3')
        self.layout.prop(context.window_manager.instancer_vars, 'level_4')
        self.layout.prop(context.window_manager.instancer_vars, 'tolerance')
        self.layout.prop(context.window_manager.instancer_vars, 'level_5')
        self.layout.prop(context.window_manager.instancer_vars, 'treshold')
        self.layout.prop(context.window_manager.instancer_vars, 'level_6')


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
