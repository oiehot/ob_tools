import bpy
from bpy.props import EnumProperty
from bpy.types import Operator

from ..functions.context import deselect_all


class SwitchModeOperator(Operator):
    bl_idname = "view3d.switch_mode_operator"
    bl_label = "Switch Mode Operator"

    selection: EnumProperty(
        items=(
            ('OBJECT', "Object", ""),
            ('VERT', "Vertex", ""),
            ('EDGE', "Edge", ""),
            ('FACE', "Face", ""),
        ),
        name="Selection",
        description="",
        default='OBJECT',
    )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if self.selection == 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
            deselect_all()
        elif self.selection == 'VERT':
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(type='VERT')
            deselect_all()
        elif self.selection == 'EDGE':
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(type='EDGE')
            deselect_all()
        elif self.selection == 'FACE':
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(type='FACE')
            deselect_all()
        else:
            return {'CANCELLED'}
        return {'FINISHED'}
