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
