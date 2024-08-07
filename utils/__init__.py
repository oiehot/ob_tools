import inspect # TODO: 블렌더 4.2에서 반복 리로드 하면 inspect를 사용하는 부분에서 예외가 발생하면서 튕긴다.
import sys
from abc import ABC
from os.path import basename, dirname

import bpy

# d:/addons/foo_tools/utils/__init__.py => foo_tools
ADDON_NAME = basename(dirname(dirname(__file__)))


def is_developer_mode() -> bool:
    return bpy.context.preferences.view.show_developer_ui


def get_current_module():
    return sys.modules[__name__]


def get_current_module_members_kv() -> list[tuple]:
    return inspect.getmembers(sys.modules[__name__])


def get_current_module_members() -> list:
    return list(map(lambda e: e[1], inspect.getmembers(sys.modules[__name__])))


def get_addon_preferences(addon_name: str):
    return bpy.context.preferences.addons[addon_name].preferences


def get_current_version() -> str:
    mod = sys.modules[ADDON_NAME]
    current_version = mod.bl_info.get("version", (0, 0, 1))
    return '.'.join([str(num) for num in current_version])


def reload_addon(addon_name: str):
    preferences = get_addon_preferences(addon_name)
    preferences_items = preferences.items()
    bpy.ops.preferences.addon_disable(module=addon_name)
    bpy.ops.preferences.addon_enable(module=addon_name)
    preferences.set_items(preferences_items)


def _line_sort(item):
    try:
        line = inspect.getsourcelines(item[1])[1]
    except:
        return 0
    return line

def is_blender_operator_class(cls):
    if getattr(cls, "bl_idname", False):
        return True
    return False

def is_abstract_class(cls):
    return issubclass(cls, ABC) and bool(getattr(cls, "__abstractmethods__", False))

def has_abstract_method(cls):
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if callable(attr) and bool(getattr(attr, "__isabstractmethod__", False)):
            return True
    return False

def register_recursive(objects) -> None:
    """재귀적으로 블렌더 클래스 등록한다.
    """
    if inspect.ismodule(objects):
        current_module_name: str = objects.__name__
        module_members = inspect.getmembers(objects)
        module_members = sorted(module_members, key=_line_sort)  # 코드 줄번호 정렬 (클래스 등록 순서)

        for key, value in module_members:

            # 포함된 하위 모듈인 경우 재귀 실행.
            # if inspect.ismodule(value) and current_module_name in value.__name__:
            #     module_name:str = value.__name__
            #     print(f"DEBUG: 모듈 등록 ({module_name})")
            #     register_recursive(value)

            # 해당 모듈에서 정의한 클래스인 경우 등록한다.
            # 추상 클래스(ABC, @abstractmethod)의 경우는 등록하지 않는다.
            if inspect.isclass(value) \
                    and type(value).__name__ == "RNAMeta" \
                    and value.__module__ == current_module_name \
                    and is_blender_operator_class(value):
                    # and not has_abstract_method(value):  # 4.2.0에서 EXCEPTION_ACCESS_VIOLATION를 발생하므로 생략.
                print(f"RegisterClass: {current_module_name}.{key}")
                bpy.utils.register_class(value)

            # 모듈에 register 함수가 있는 겨우 실행한다.
            if key == "register" and callable(value):
                value()

            # 모듈에 REGISTER_MODULES 있는 경우 재귀 실행.
            if key == "REGISTER_CLASSES":
                register_recursive(value)
    else:
        # 모듈이 아니면 클래스나 리스트다.
        # 튜플의 경우 항목이 1개면 tuple타입이 안되므로 리스트로 변경한다.
        if type(objects) not in [list, tuple, set]:
            objects = [objects]

        # 리스트를 순회하며 모듈이면 재귀하고 클래스면 등록한다.
        for obj in objects:
            if inspect.ismodule(obj):
                register_recursive(obj)
            elif inspect.isclass(obj):
                print(f"RegisterClass: {obj}")
                bpy.utils.register_class(obj)


def unregister_recursive(objects) -> None:
    """재귀적으로 블렌더 클래스를 해제한다.
    """
    if inspect.ismodule(objects):
        current_module_name: str = objects.__name__
        module_members = inspect.getmembers(objects)
        for key, value in module_members:

            # 해당 모듈에서 정의한 클래스인 경우 등록 해제한다.
            if inspect.isclass(value) \
                and type(value).__name__ == "RNAMeta" \
                and value.__module__ == current_module_name \
                and is_blender_operator_class(value):
                # and not has_abstract_method(value):  # 4.2.0에서 EXCEPTION_ACCESS_VIOLATION를 발생하므로 생략.
                print(f"UnregisterClass: {current_module_name}.{key}")
                bpy.utils.unregister_class(value)

            # 모듈에 unregister 함수가 있는 경우 실행한다.
            if key == "unregister" and callable(value):
                value()

            # 모듈에 REGISTER_MODULES 있는 경우 재귀 실행.
            if key == "REGISTER_CLASSES":
                unregister_recursive(value)
    else:
        # 모듈이 아니면 클래스나 리스트다.
        # 튜플의 경우 항목이 1개면 tuple타입이 안되므로
        if type(objects) not in [list, tuple, set]:
            objects = [objects]

        # 집합이면 reverse가 안되므로 리스트로 바꾼다.
        if type(objects) is set:
            objects = list(objects)
        objects = reversed(objects)

        # 리스트를 순회하며 모듈이면 재귀하고 클래스면 등록해제한다.
        for obj in objects:
            if inspect.ismodule(obj):
                unregister_recursive(obj)
            elif inspect.isclass(obj):
                print(f"UnregisterClass: {obj}")
                bpy.utils.unregister_class(obj)
