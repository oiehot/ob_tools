import bpy
from bpy.props import StringProperty, FloatProperty, FloatVectorProperty, BoolProperty
from bpy.types import Object, TextCurve

from ..functions.context import is_object_mode
from ..utils.math_utils import deg_to_rad_tuple


class CreateText(bpy.types.Operator):
    """텍스트 오브젝트를 생성한다.
    """
    bl_idname = "object.create_text"
    bl_label = "Create Text Object"

    text: StringProperty(name="Text", default="Hello World")
    radius: FloatProperty(name="Radius", default=1.0)
    location: FloatVectorProperty(name="Location", default=(0.0, 0.0, 0.0))
    rotation: FloatVectorProperty(name="Rotation", default=(90.0, 0.0, 0.0))
    scale: FloatVectorProperty(name="Scale", default=(0.0, 0.0, 0.0))
    hide_render: BoolProperty(name="Hide Render", default=True)

    @classmethod
    def poll(cls, context):
        return True if is_object_mode() else False

    def execute(self, context):
        bpy.ops.object.text_add(
            radius=self.radius,
            enter_editmode=False,
            align="WORLD",
            location=self.location,
            rotation=deg_to_rad_tuple(self.rotation),
            scale=self.scale
        )

        # Text Object
        obj: Object = bpy.context.object
        assert obj and obj.type == "FONT"
        obj.hide_render = self.hide_render

        # Text Data
        text: TextCurve = obj.data
        text.body = self.text
        text.align_x = "LEFT"
        text.align_y = "TOP"
        text.space_line = 1

        return {"FINISHED"}
