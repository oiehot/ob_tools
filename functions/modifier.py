import bpy
from bpy.types import Object, Modifier, LatticeModifier


def apply_modifier(obj: Object, modifier_name: str) -> bool:
    """오브젝트의 특정 모디파이어를 적용apply 시킨다.
    """
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)

    if modifier_name in obj.modifiers:
        bpy.ops.object.modifier_apply(modifier=modifier_name)
        return True
    else:
        return False


def remove_modifier(obj: Object, modifier_name: str) -> bool:
    """오브젝트의 특정 모디파이어를 제거remove 한다.
    """
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)

    if modifier_name in obj.modifiers:
        bpy.ops.object.modifier_remove(modifier=modifier_name)
        return True
    else:
        return False


def has_modifier(obj: Object, modifier_name: str) -> bool:
    return True if modifier_name in obj.modifiers else False


def get_modifier_by_name(obj: Object, modifier_name: str) -> Modifier | None:
    if modifier_name in obj.modifiers:
        return obj.modifiers[modifier_name]
    else:
        return None


def get_lattice_modifier_vertex_group(lattice_modifier: LatticeModifier) -> str | None:
    result: str = lattice_modifier.vertex_group
    return result if result != "" else None
