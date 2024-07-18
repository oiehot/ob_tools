from . import (menus, operators, panels, keymaps)
from .utils import register_recursive, unregister_recursive
from .utils.module import unload_all_modules

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
