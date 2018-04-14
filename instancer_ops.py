# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#   https://github.com/Korchy/1d_instancer
#
# Version history:
#   1.0. - research


import bpy
from .instancer import Instancer


class InstancerSearch(bpy.types.Operator):
    bl_idname = 'instancer.search'
    bl_label = 'Search fro instances'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Instancer.search_for_instances(context)
        return {'FINISHED'}



def register():
    bpy.utils.register_class(InstancerSearch)


def unregister():
    bpy.utils.unregister_class(InstancerSearch)
