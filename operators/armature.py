import bpy
from bpy.props import EnumProperty
from bpy.types import Operator

from ..functions.context import (
    deselect_all, select_object, select_objects, set_active_object
)
from ..functions.rigging import (
    set_bone_collections_visible,
    set_all_bone_collections_visible,
    has_armature_modifier,
    get_armature_modifier,
    get_selected_armatures,
)

RIGIFY_BONE_COLLECTIONS: list[str] = [
    "Face",
    "Face (Primary)",
    "Face (Secondary)",
    "Torso",
    "Torso (Tweak)",
    "Fingers",
    "Fingers (Detail)",
    "Arm.L (IK)",
    "Arm.L (FK)",
    "Arm.L (Tweak)",
    "Arm.R (IK)",
    "Arm.R (FK)",
    "Arm.R (Tweak)",
    "Leg.L (IK)",
    "Leg.L (FK)",
    "Leg.L (Tweak)",
    "Leg.R (IK)",
    "Leg.R (FK)",
    "Leg.R (Tweak)",
    "Root",
    "ORG",
    "MCH",
    "DEF"
]

RIGIFY_UNUSED_BONE_COLLECTIONS: list[str] = [
    "ORG",
    "MCH"
]

RIGIFY_CONTROLLER_COLLECTIONS: list[str] = [
    "Face",
    "Torso",
    "Fingers",
    "Arm.L (IK)",
    "Arm.R (IK)",
    "Leg.L (IK)",
    "Leg.R (IK)",
]

RIGIFY_DEF_COLLECTIONS: list[str] = [
    "DEF"
]


class ToggleWeightPaintMode(Operator):
    """선택된 MeshObject의 WeightPaint모드로 쉽게 전환한다.
    Rigify로 만들어진 RIG-Armature의 경우 편집하면서 포즈를 바꾸기 용이하도록 컨트롤러와 본만 보이게 만든다.
    """

    bl_idname = "armature.toggle_weight_paint_mode"
    bl_label = "Toggle Weight Paint Mode"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        """선택된 오브젝트 중에서 하나의 MeshObject 그리고 연관된 하나의 Armature가 있어야 한다.
        """
        mesh_objects = [obj for obj in bpy.context.selected_objects if obj.type == "MESH"]
        armatures = [get_armature_modifier(obj).object.data for obj in mesh_objects if has_armature_modifier(obj) if
                     get_armature_modifier(obj).object]
        return True if len(mesh_objects) == 1 and len(armatures) == 1 else False

    def execute(self, context):
        if bpy.context.mode == "PAINT_WEIGHT":
            bpy.ops.object.mode_set(mode="OBJECT")

            mesh_objects = [obj for obj in bpy.context.selected_objects if obj.type == "MESH"]
            mesh_object = mesh_objects[0]
            deselect_all()
            select_object(mesh_object)
            set_active_object(mesh_object)

            # Armature의 BoneCollection을 ObjectMode에 맞게 설정한다.
            armature = get_armature_modifier(mesh_object).object.data
            set_all_bone_collections_visible(armature, False)
            set_bone_collections_visible(armature,
                                         list(set(RIGIFY_BONE_COLLECTIONS) - set(RIGIFY_UNUSED_BONE_COLLECTIONS)), True)
        else:
            mesh_objects = [obj for obj in bpy.context.selected_objects if obj.type == "MESH"]
            assert (len(mesh_objects) == 1)
            mesh_object = mesh_objects[0]
            armature_objects = [get_armature_modifier(obj).object for obj in mesh_objects if has_armature_modifier(obj)
                                if get_armature_modifier(obj).object]
            armature_object = armature_objects[0]

            # Armature의 BoneCollection을 PaintWeightMode 맞게 설정한다.
            armature = armature_object.data
            set_all_bone_collections_visible(armature, False)
            set_bone_collections_visible(armature,
                                         list(set(RIGIFY_CONTROLLER_COLLECTIONS) | set(RIGIFY_DEF_COLLECTIONS)), True)

            deselect_all()
            select_objects([armature_object, mesh_object])
            set_active_object(mesh_object)
            bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
        return {"FINISHED"}


class ToggleBoneCollectionVisible(Operator):
    """선택된 Armature Object의 본 콜렉션 Visible을 특정 모드로 토글한다.
    """
    bl_idname = "armature.toggle_bone_collection_visible"
    bl_label = "Toggle Bone Collection Visible"
    bl_options = {"REGISTER", "UNDO"}

    mode: EnumProperty(
        name="Mode",
        items=(
            ("ALL", "All", "Visible All"),
            ("DEFAULT", "Default", "Visible Bones and Controllers"),
            ("BONES", "Bone", "Visible Bones Only"),
            ("NONE", "None", "Visible None"),
        )
    )

    @classmethod
    def poll(cls, context):
        """선택된 오브젝트 중 Armature 타입의 Object가 있는 경우에는 실행 가능하다.
        """
        armatures = get_selected_armatures()
        return True if len(armatures) > 0 else False

    def execute(self, context):
        armatures = get_selected_armatures()
        for armature in armatures:
            set_all_bone_collections_visible(armature, False)
            match self.mode:
                case "ALL":
                    set_all_bone_collections_visible(armature, True)
                case "DEFAULT":
                    set_bone_collections_visible(armature,
                                                 list(set(RIGIFY_CONTROLLER_COLLECTIONS) | set(RIGIFY_DEF_COLLECTIONS)),
                                                 True)
                case "CONTROLLERS":
                    set_bone_collections_visible(armature, RIGIFY_CONTROLLER_COLLECTIONS, True)
                case "BONES":
                    set_bone_collections_visible(armature, RIGIFY_DEF_COLLECTIONS, True)
                case "NONE":
                    pass
                case _:
                    pass
        return {"FINISHED"}
