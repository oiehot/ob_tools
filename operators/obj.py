import json
import bpy
from bpy.types import Operator

from ..functions.context import is_object_mode, has_selected_objects


class ResetOriginPosition(Operator):
    bl_idname = "object.reset_origin_position"
    bl_label = "Reset Origin Position"

    @classmethod
    def poll(cls, context):
        return True if is_object_mode() and has_selected_objects() else False

    def execute(self, context):
        new_origin = (0, 0, 0)
        old_cursor = context.scene.cursor.location
        context.scene.cursor.location = new_origin
        bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
        context.scene.cursor.location = old_cursor
        return {"FINISHED"}


class DeleteProperties(Operator):
    """
    선택된 모든 오브젝트의 커스텀 프로퍼티를 삭제한다.
    """
    bl_idname = "object.delete_properties"
    bl_label = "Delete All Properties"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        """선택된 오브젝트가 없거나, 선택된 오브젝트들에 커스텀 프로퍼티가 없는 경우 False
        """
        if not context.selected_objects:
            return False
        for obj in context.selected_objects:
            for key in obj.keys():
                if key not in "_RNA_UI":
                    return True
        return False

    def execute(self, context):
        for obj in context.selected_objects:
            for prop in list(obj.keys()):
                if prop not in "_RNA_UI":
                    del obj[prop]
        return {"FINISHED"}


class ExportProperties(Operator):
    """
    선택된 모든 오브젝트의 커스텀 프로퍼티를 JSON 형식으로 Export한다.
    """
    bl_idname = "object.export_properties_json"
    bl_label = "Export Properties to JSON"
    bl_options = {"REGISTER", "UNDO"}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        """선택된 오브젝트가 없거나, 선택된 오브젝트들에 커스텀 프로퍼티가 없는 경우 False
        """
        if not context.selected_objects:
            return False
        for obj in context.selected_objects:
            for key in obj.keys():
                if key not in "_RNA_UI":
                    return True
        return False

    def execute(self, context):
        data = {}
        for obj in context.selected_objects:
            data[obj.name] = {key: obj[key] for key in obj.keys() if key not in "_RNA_UI"}

        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class ImportProperties(Operator):
    """
    JSON 데이터를 현재 씬의 오브젝트에 Import한다.
    """
    bl_idname = "object.import_properties"
    bl_label = "Import Properties"
    bl_options = {"REGISTER", "UNDO"}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    replace: bpy.props.BoolProperty(name="Replace Existing", default=True)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        with open(self.filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        for obj_name, props in data.items():
            obj = bpy.data.objects.get(obj_name)
            if obj:
                if self.replace:
                    for key in list(obj.keys()):
                        if key not in "_RNA_UI":
                            del obj[key]
                for key, value in props.items():
                    obj[key] = value

        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
