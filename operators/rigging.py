import bpy
from bpy.props import BoolProperty, StringProperty
from bpy.types import Object, Operator, Collection, Armature

from ..functions.context import (
    get_selected_objects, get_selected_object_by_type, get_selected_objects_by_type,
    select_objects, deselect_all,
    set_active_object,
    is_object_mode,
)
from ..functions.rigging import (
    is_rig_attached, detach_rigmesh, attach_rigmesh,
    remove_armature_modifiers, remove_vertex_groups,
    save_object_vertex_groups, load_object_vertex_groups,
    has_vertex_groups
)


class DetachRigMesh(Operator):
    """선택된 MeshObject를 리깅에서 제외시킨다.
    """
    bl_idname = "object.detach_rig_mesh"
    bl_label = "Detach Rig Mesh"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        attached_objects = [obj for obj in get_selected_objects() if is_rig_attached(obj)]
        if len(attached_objects) > 0:
            return True
        return False

    def execute(self, context):
        attached_objects = [obj for obj in get_selected_objects() if is_rig_attached(obj)]
        for obj in attached_objects:
            detach_rigmesh(obj)
        return {'FINISHED'}


class AttachRigMesh(Operator):
    """선택된 MeshObject와 Armature를 연결한다.
    """
    bl_idname = "object.attach_rig_mesh"
    bl_label = "Attach Rig Mesh"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        mesh_objects = get_selected_objects_by_type("MESH")
        armature = get_selected_object_by_type("ARMATURE")
        detached_objects = [obj for obj in mesh_objects if not is_rig_attached(obj)]
        if armature and len(detached_objects) > 0:
            return True
        else:
            return False

    def execute(self, context):
        mesh_objects = get_selected_objects_by_type("MESH")
        armature = get_selected_object_by_type("ARMATURE")
        detached_objects = [obj for obj in mesh_objects if not is_rig_attached(obj)]
        for obj in detached_objects:
            attach_rigmesh(obj, modifier_name="Armature", armature=armature)
        return {'FINISHED'}


class RemoveGeneratedRig(Operator):
    """Armature Rigify Generate Rig로 생성된 Collection과 Armature를 제거한다.
    """
    bl_idname = "object.remove_generated_rig"
    bl_label = "Remove Generated Rig"
    bl_options = {"REGISTER", "UNDO"}

    clear_armature_modifier: BoolProperty(
        name="Clear Armature Modifier",
        description="Clear null armature modifier",
        default=True
    )
    clear_vertex_group: BoolProperty(
        name="Clear Vertex Group",
        description="Clear remain vertex groups",
        default=True
    )

    @classmethod
    def poll(cls, context):
        has_wgts: bool = False
        has_rig_armature: bool = False

        # WGTS_로 시작하는 콜렉션이 있다면
        for collection in bpy.data.collections:
            if collection.name.startswith("WGTS_"):
                has_wgts = True

        # RIG-로 시작하는 Armature가 있다면 True
        armatures: list[Armature] = [obj for obj in bpy.data.objects if obj.type == "ARMATURE"]
        for armature in armatures:
            if armature.name.startswith("RIG-"):
                has_rig_armature = True

        return has_wgts or has_rig_armature

    def _remove_rig_armature(self, armature: Armature):
        """RIG-로 시작하는 Armature를 제거한다.
        동시에 Armature에 Parent되어 있던 Mesh Object들을 Unparent하고
        Mesh Object에 남겨진 ArmatureModifier와 VertexGroup등을 옵션에 따라 제거한다.
        """
        mesh_objects: list[Object] = [obj for obj in armature.children if obj.type == "MESH"]
        for obj in mesh_objects:
            # RIG-Armature에 Parent되어있던 Mesh들을 Unparent한다.
            obj.parent = None

            # 필요시 Armature Modifier를 제거한다.
            # 참고로 RIG-Armature가 제거되면 이 Modifier의 object 프로퍼티는 Null이 된 상태로 유지된다.
            if self.clear_armature_modifier:
                remove_armature_modifiers(obj)

            # 필요시 VertexGroup를 제거한다.
            if self.clear_vertex_group:
                remove_vertex_groups(obj)

        # 마지막으로 Rig-Armature를 제거한다.
        bpy.data.objects.remove(armature)

    def _remove_wgts_collection(self, collection: Collection):
        """GenerateRig시 생성되는 위젯들의 콜렉션을 제거한다.
        """
        bpy.data.collections.remove(collection)

    def execute(self, context):
        # RIG-로 시작하는 Armature를 제거한다.
        armatures: list[Armature] = [obj for obj in bpy.data.objects if obj.type == "ARMATURE"]
        for armature in armatures:
            if armature.name.startswith("RIG-"):
                self._remove_rig_armature(armature)

        # WGTS_로 시작하는 Collection을 제거한다.
        for collection in bpy.data.collections:
            if collection.name.startswith("WGTS_"):
                self._remove_wgts_collection(collection)

        return {"FINISHED"}


class GenerateRigFromArmature(Operator):
    """선택된 베이스 Armature를 이용하여 Rigify Rig Armature를 생성한다.
    """
    bl_idname = "object.generate_rig_from_armature"
    bl_label = "Generate Rig From Armature"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        # 1개의 Armature가 선택되어 있어야 한다. (2개 이상이면 안된다)
        armature_objects = get_selected_objects_by_type("ARMATURE")
        if len(armature_objects) != 1:
            return False

        # Armature의 이름이 RIG-로 시작하면 안된다.
        armature_object: Armature = armature_objects[0]
        if armature_object.name.startswith("RIG-"):
            return False

        return True

    def execute(self, context):
        armature_objects: list[Object] = get_selected_objects_by_type("ARMATURE")
        base_armature: Armature = armature_objects[0]

        # 선택된 Mesh, Armature를 통해 Rigify Generate 실행한다.
        bpy.ops.pose.rigify_generate()

        # 베이스 Armature는 Hidden 시킨다.
        base_armature.hide_select = True
        base_armature.hide_viewport = True
        base_armature.hide_render = True

        return {"FINISHED"}


class AutoSkin(Operator):
    """선택된 RIG-Armature와 Mesh들을 자동으로 Skin 해준다.
    """
    bl_idname = "object.auto_skin"
    bl_label = "Auto Skin"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        # 1개 이상의 Mesh Object와
        mesh_objects = get_selected_objects_by_type("MESH")
        if len(mesh_objects) < 1:
            return False

        # 1개의 Armature가 선택되어 있어야 한다. (2개 이상이면 안된다)
        armature_objects = get_selected_objects_by_type("ARMATURE")
        if len(armature_objects) != 1:
            return False

        # Armature의 이름이 RIG-로 시작해야 한다.
        # BaseArmature가 아닌 Rigify로 생성된 RIG-Armature에 Skin되도록 유도하는 것이다.
        # rig_armature: Armature = armature_objects[0]
        # if not rig_armature.name.startswith("RIG-"):
        #     return False

        return True

    def execute(self, context):
        mesh_objects: list[Object] = get_selected_objects_by_type("MESH")
        armature_objects: list[Object] = get_selected_objects_by_type("ARMATURE")
        rig_armature_object = armature_objects[0]

        # Select된 오브젝트들이 Active 오브젝트로 Parent된다.
        deselect_all()
        select_objects(mesh_objects)
        set_active_object(rig_armature_object)

        # 선택된 Mesh, Armature를 통해 Auto Skin 실행.
        # rigging_grid.operator("object.parent_set", text="Auto Skin").type = "ARMATURE_AUTO"
        bpy.ops.object.parent_set(type="ARMATURE_AUTO")

        return {"FINISHED"}


class SaveObjectVertexGroups(Operator):
    """현재 선택된 오브젝트의 VertexGroup들의 정보를 주어진 경로에 저장한다.
    """
    bl_idname = "object.save_object_vertex_groups"
    bl_label = "Save Object Vertex Groups"
    bl_options = {"REGISTER", "UNDO"}

    # 💡 filter_glob 이라는 프로퍼티를 정의해두면 window_manager.fileselect_add()에서 확장자 필터링으로 사용된다.
    filter_glob: bpy.props.StringProperty(
        default="*.json",
        options={"HIDDEN"}
    )

    # ⚠️ 이름이 filepath 이어야만 context.window_manager.fileselect_add()에 의해 값이 잘 저장된다.
    filepath: StringProperty(
        name="Filepath",
        description="Save filepath",
        subtype="FILE_PATH"
    )

    @classmethod
    def poll(cls, context):
        obj = bpy.context.active_object
        if is_object_mode() and obj and has_vertex_groups(obj):
            return True
        else:
            return False

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        if not self.filepath:
            self.report({"ERROR"}, f"Invalid path (path: {self.filepath})")
            return {"CANCELLED"}

        obj = bpy.context.active_object
        if save_object_vertex_groups(obj=obj, path=self.filepath):
            self.report({"INFO"}, f"File saved (path: {self.filepath})")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, f"Save failed (path: {self.filepath})")
            return {"CANCELLED"}


class LoadObjectVertexGroups(Operator):
    """주어진 경로에 저장되어있는 VertexGroup들의 정보를 현재 선택 오브젝트로 로드한다.
    기존 VertexGroup들의 정보는 덮어쓰기 된다.
    """
    bl_idname = "object.load_object_vertex_groups"
    bl_label = "Load Object Vertex Groups"
    bl_options = {"REGISTER", "UNDO"}

    # 💡 filter_glob 이라는 프로퍼티를 정의해두면 window_manager.fileselect_add()에서 확장자 필터링으로 사용된다.
    filter_glob: bpy.props.StringProperty(
        default="*.json",
        options={"HIDDEN"}
    )

    # ⚠️ 이름이 filepath 이어야만 context.window_manager.fileselect_add()에 의해 값이 잘 저장된다.
    filepath: StringProperty(
        name="Filepath",
        description="Load filepath",
        subtype="FILE_PATH"
    )

    @classmethod
    def poll(cls, context):
        if bpy.context.active_object:
            return True
        else:
            return False

    def invoke(self, context, event):
        # return context.window_manager.invoke_props_dialog(self)
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        if not self.filepath:
            self.report({"ERROR"}, f"Invalid path (path: {self.filepath})")
            return {"CANCELLED"}

        obj = bpy.context.active_object
        if load_object_vertex_groups(path=self.filepath, obj=obj):
            self.report({"INFO"}, f"File loaded (path: {self.filepath}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, f"Load failed (path: {self.filepath})")
            return {"CANCELLED"}
