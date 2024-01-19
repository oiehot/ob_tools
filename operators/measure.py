import os

from bpy.props import EnumProperty
from bpy.types import Operator
from ..functions.viewport import set_editmode_overlay_type


class SetEditModeOverlayType(Operator):
    """편집모드 오버레이 타입을 변경한다.
    """
    bl_idname = "view3d.set_editmode_overlay_type"
    bl_label = "Set EditMode Overlay Type"

    mode: EnumProperty(
        name="Mode",
        items=(
            ("DEFAULT", "Default", "Default Mode"),
            ("MEASURE", "Measure", "Measure Mode"),
            ("INTERSECT", "Intersect", "Intersect Analysis Mode"),
            ("DISTORT", "Distortion", "Distortion Analysis Mode"),
            ("DEVELOP", "Development", "Development Mode")
        ),
        default="DEFAULT"
    )

    @classmethod
    def poll(cls, context):
        return True if context.scene and context.scene.render else False

    def execute(self, context):
        set_editmode_overlay_type(context, self.mode)
        return {"FINISHED"}
