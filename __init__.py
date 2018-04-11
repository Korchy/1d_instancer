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

from . import instancer_panel
from . import instancer_ops
from . import instancer


def register():
    instancer_ops.register()
    instancer_panel.register()


def unregister():
    instancer_panel.unregister()
    instancer_ops.unregister()


if __name__ == '__main__':
    register()
