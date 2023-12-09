from . import (menus, operators, panels, keymaps)
from .utils import register_recursive, unregister_recursive
from .utils.module import unload_all_modules

bl_info = {
    "name": "OB Tools",
    "description": "",
    "author": "oiehot@gmail.com",
    "version": (0, 1, 0),
    "blender": (4, 0, 2),
    "location": "",
    "wiki_url": "",
    "tracker_url": "",
    "warning": "",
    "doc_url": "",
    "category": "Generic"
}

REGISTER_CLASSES = (
    menus,
    operators,
    panels,
    keymaps
)


def register():
    register_recursive(REGISTER_CLASSES)


def unregister():
    unregister_recursive(REGISTER_CLASSES)

    # Development Only
    try:
        unload_all_modules('ob_tools')
    except:
        pass


if __name__ == "__main__":
    register()
