from abc import ABC, abstractmethod

import bpy
from bpy.props import EnumProperty, IntProperty, FloatProperty
from bpy.types import Object, Operator, LatticeModifier

from ..functions.context import is_object_mode, is_editmesh_mode, get_selected_objects
from ..functions.mesh import remove_vertex_group
from ..functions.modifier import apply_modifier, remove_modifier, get_modifier_by_name
from ..functions.obj import delete_object

LATTICE_MODIFIER_NAME = "SimpleLattice"


def _get_related_objects_from_lattice_object(lattice_object: Object) -> list[Object]:
    """LatticeObject와 연결된 MeshObject들을 리턴한다.
    """
    results: list[Object] = []
    for obj in bpy.data.objects:
        for modifier in obj.modifiers:
            if modifier.type == "LATTICE" and modifier.object == lattice_object and modifier.name == LATTICE_MODIFIER_NAME:
                results.append(obj)
    return results


def _get_lattice_object_from_mesh_object(obj: Object) -> Object | None:
    """MeshObject의 LatticeModifier에 연결된 Lattice오브젝트를 리턴한다.
    """
    assert (obj.type == "MESH")
    for modifier in obj.modifiers:
        if modifier.type == "LATTICE" and modifier.name == LATTICE_MODIFIER_NAME:
            return modifier.object
    return None


def _is_lattice_object(obj: Object) -> bool:
    """Lattice오브젝트인가?
    """
    return True if obj.type == "LATTICE" else False


def _is_lattice_assigned_mesh_object(obj: Object) -> bool:
    """Lattice 모디파이어를 사용 중인가?
    """
    if obj.type == "MESH":
        for modifier in obj.modifiers:
            if modifier.type == "LATTICE" and modifier.name == LATTICE_MODIFIER_NAME:
                return True
    return False


def _get_lattice_object_user_count(lattice_object: Object) -> int:
    """이 Lattice오브젝트를 모디파이어에서 참조하는 다른 오브젝트들의 수를 리턴한다.
    """
    count: int = 0
    for obj in bpy.data.objects:
        for modifier in obj.modifiers:
            if modifier.type == "LATTICE" and modifier.object == lattice_object and modifier.name == LATTICE_MODIFIER_NAME:
                count += 1
    return count


def apply_quick_lattice_modifier_decorator(func):
    def wrapper(obj: Object, *args, **kwargs):
        assert (obj.type == "MESH")
        modifier: LatticeModifier = get_modifier_by_name(obj, LATTICE_MODIFIER_NAME)
        if modifier:
            vg_name: str = modifier.vertex_group
            # apply_modifier(obj, LATTICE_MODIFIER_NAME)
            func(obj, *args, **kwargs)
            if vg_name != "":
                remove_vertex_group(obj, vg_name)

    return wrapper


@apply_quick_lattice_modifier_decorator
def _apply_quick_lattice_modifier(obj: Object):
    """Lattice모디파이어를 적용시킨다.
    """
    apply_modifier(obj, LATTICE_MODIFIER_NAME)


@apply_quick_lattice_modifier_decorator
def _remove_quick_lattice_modifier(obj: Object):
    """Lattice모디파이러를 적용하지 않고 제거한다.
    """
    remove_modifier(obj, LATTICE_MODIFIER_NAME)


class CreateQuickLattice(Operator):
    """QuickLattice

    """
    bl_idname = "object.create_quick_lattice"
    bl_label = "Quick Lattice"
    bl_options = {"REGISTER", "UNDO"}

    orientation: EnumProperty(
        name="Orientation",
        items=(
            ("GLOBAL", "Global", ""),
            ("LOCAL", "Local", ""),
            ("CURSOR", "Cursor", ""),
            ("NORMAL", "Normal", "")
        ),
        default="NORMAL"
    )
    resolution_u: IntProperty(name="U", default=3, min=2)
    resolution_v: IntProperty(name="V", default=3, min=2)
    resolution_w: IntProperty(name="W", default=3, min=2)
    rotation_x: FloatProperty(name="X", subtype="ANGLE", default=0.0, step=100.0, precision=4, options={"SKIP_SAVE"})
    rotation_y: FloatProperty(name="Y", subtype="ANGLE", default=0.0, step=100.0, precision=4, options={"SKIP_SAVE"})
    rotation_z: FloatProperty(name="Z", subtype="ANGLE", default=0.0, step=100.0, precision=4, options={"SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        """오브젝트 모드 또는 에디트 모드여야 하며, MeshObject를 1개 이상 선택한 상태여야 하고, 선택된 오브젝트 전부 Lattice가 없어야 함.
        """
        objects = get_selected_objects()
        selected_mesh_objects = [obj for obj in objects if obj.type == "MESH"]
        lattice_related_objects = [obj for obj in objects if
                                   _is_lattice_object(obj) or _is_lattice_assigned_mesh_object(obj)]
        return True if (is_object_mode() or is_editmesh_mode()) and len(selected_mesh_objects) > 0 and len(
            lattice_related_objects) <= 0 else False

    def execute(self, context):
        # TODO: 지금은 SimpleQuickLattice를 사용해서 생성하지만 추후에는 자체 오퍼레이터로 해결할 수 있어야 함.
        try:
            bpy.ops.object.op_lattice_create(
                orientation=self.orientation,
                ignore_mods=False,
                resolution_u=self.resolution_u, resolution_v=self.resolution_v, resolution_w=self.resolution_w,
                interpolation="KEY_LINEAR",
                scale=1, tweak_angles=False,
                rot_x=self.rotation_x, rot_y=self.rotation_y, rot_z=self.rotation_z
            )
        except:
            self.report({"ERROR"}, f"SimpleQuickLattice Required (https://github.com/BenjaminSauder/SimpleLattice)")
            return {"CANCELLED"}
        return {"FINISHED"}


class ModifyQuickLattice(Operator):
    """선택된 오브젝트와 관련된 LatticeModifier를 적용 또는 제거를 위해 만들어진 상속용 베이스 클래스.
    """

    @abstractmethod
    def modify(self, obj):
        raise NotImplementedError

    @classmethod
    def poll(cls, context):
        """오브젝트 모드여야 하며, 선택된 오브젝트 중 한 개 이상의 Lattice관련 오브젝트가 있어야 함.
        """
        objects = get_selected_objects()
        lattice_related_objects = [obj for obj in objects if
                                   _is_lattice_object(obj) or _is_lattice_assigned_mesh_object(obj)]
        return True if is_object_mode() and len(lattice_related_objects) > 0 else False

    def execute(self, context):
        selected_objects = get_selected_objects()

        # 선택된 것들 중 LatticeControlObject가 있다면 연결된 MeshObject들을 얻는다.
        objects_from_selected_lattice_objects = []
        for obj in selected_objects:
            if _is_lattice_object(obj):
                objects_from_selected_lattice_objects.extend(_get_related_objects_from_lattice_object(obj))

        # 선택된 것들 중 MeshObject가 있다면 Lattice가 적용된것들만 모은다.
        mesh_objects_from_selection = [obj for obj in selected_objects if _is_lattice_assigned_mesh_object(obj)]

        # 이후에 제거하기 위한 LatticeControlObject들을 모은다.
        lattice_objects_a = [obj for obj in selected_objects if _is_lattice_object(obj)]
        lattice_objects_b = [_get_lattice_object_from_mesh_object(obj) for obj in mesh_objects_from_selection]
        lattice_objects = set(lattice_objects_a) | set(lattice_objects_b)

        # Mesh오브젝트들의 Modifier를 적용Apply 또는 제거Remove 한다.
        objects = set(objects_from_selected_lattice_objects) | set(mesh_objects_from_selection)
        for obj in objects:
            self.modify(obj)

        # 불필요해진 LatticeControlObject들을 제거한다.
        unused_lattice_objects = [obj for obj in lattice_objects if _get_lattice_object_user_count(obj) <= 0]
        for obj in unused_lattice_objects:
            delete_object(obj)

        return {"FINISHED"}


class ApplyQuickLattice(ModifyQuickLattice):
    """선택된 오브젝트와 관련된 LatticeModifier를 적용하고 정리한다.
    """
    bl_idname = "object.apply_quick_lattice"
    bl_label = "Apply Quick Lattice"
    bl_options = {"REGISTER", "UNDO"}

    def modify(self, obj):
        _apply_quick_lattice_modifier(obj)


class RemoveQuickLattice(ModifyQuickLattice):
    """선택된 오브젝트와 관련된 LatticeModifier를 제거하고 정리한다.
    """
    bl_idname = "object.remove_quick_lattice"
    bl_label = "Remove Quick Lattice"
    bl_options = {"REGISTER", "UNDO"}

    def modify(self, obj):
        _remove_quick_lattice_modifier(obj)
