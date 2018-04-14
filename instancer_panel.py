# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#   https://github.com/Korchy/1d_instancer
#
# Version history:
#   1.0. - research


import bpy


class InstancerPanel(bpy.types.Panel):
    bl_idname = 'instancer.panel'
    bl_label = 'Instancer'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = '1D'

    def draw(self, context):
        self.layout.operator('instancer.search', icon='FULLSCREEN_EXIT', text='Collaps to instances')
        self.layout.prop(context.window_manager.instancer_vars, 'vector_bit')


def register():
    bpy.utils.register_class(InstancerPanel)


def unregister():
    bpy.utils.unregister_class(InstancerPanel)
