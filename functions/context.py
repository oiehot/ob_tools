import bpy
from bpy.types import Object


def set_mode(mode: str) -> None:
    bpy.ops.object.mode_set(mode=mode)


def get_mode() -> str:
    return bpy.context.mode


def set_object_mode() -> None:
    bpy.ops.object.mode_set(mode="OBJECT")


def set_edit_mode() -> None:
    bpy.ops.object.mode_set(mode="EDIT")


def set_paint_weight_mode() -> None:
    bpy.ops.object.mode_set(mode="PAINT_WEIGHT")


def is_object_mode() -> bool:
    return True if get_mode() == "OBJECT" else False


def is_edit_mode() -> bool:
    return True if get_mode() == "EDIT" else False


def set_active_object(obj: Object):
    bpy.context.view_layer.objects.active = obj


def get_active_object() -> Object | None:
    return bpy.context.active_object


def deactive():
    bpy.context.view_layer.objects.active = None


def get_selected_object() -> Object | None:
    objects = bpy.context.selected_objects
    if len(objects) > 0:
        return objects[0]
    return None


def get_selected_objects() -> list[Object]:
    return bpy.context.selected_objects


def get_selected_objects_by_type(type_str: str) -> list[Object]:
    return [obj for obj in bpy.context.selected_objects if obj.type == type_str]


def get_selected_object_by_type(type_str: str) -> Object | None:
    objects = get_selected_objects_by_type(type_str)
    if len(objects) > 0:
        return objects[0]
    else:
        return None


def is_component_selected() -> bool:
    if not has_selected_objects() and has_active_objects() is not None and is_edit_mode():
        return True
    return False


def has_active_objects() -> bool:
    return True if bpy.context.active_object else False


def has_selected_objects() -> bool:
    return True if len(bpy.context.selected_objects) > 0 else False


def select_all():
    raise NotImplementedError


def select_object(obj: Object):
    obj.select_set(True)


def select_objects(objects: list[Object]):
    for obj in objects:
        obj.select_set(True)


def select_object_by_type(type_str: str):
    raise NotImplementedError


def deselect_object(obj: Object):
    obj.select_set(False)


def deselect_objects(objects: list[Object]):
    for obj in objects:
        obj.select_set(False)


def deselect_all(deactive=True) -> None:
    # Deactive
    if deactive and bpy.context.active_object:
        # bpy.context.active_object.select_set(False)
        bpy.context.view_layer.objects.active = None
    # Deselect All
    try:
        bpy.ops.object.select_all(action="DESELECT")
    except:
        pass


def edit_mode(func):
    """Edit모드에서 함수를 실행하는 데코레이터
    """

    def wrapper(*args, **kwargs):
        previous_mode: str = get_mode()
        set_edit_mode()
        result = func(*args, **kwargs)
        set_mode(previous_mode)
        return result

    return wrapper


def object_mode(func):
    """Object모드에서 함수를 실행하는 데코레이터
    """

    def wrapper(*args, **kwargs):
        previous_mode: str = get_mode()
        set_object_mode()
        result = func(*args, **kwargs)
        set_mode(previous_mode)
        return result

    return wrapper
