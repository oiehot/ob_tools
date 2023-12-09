import bpy
from bpy.props import EnumProperty
from bpy.types import Operator


class AlignAxisAverageOperator(Operator):
    bl_idname = "align.axis_average"
    bl_label = "Align to X, Y, Z"
    bl_description = "Align Selected Along the chosen axis"
    bl_options = {'REGISTER', 'UNDO'}

    axis: EnumProperty(
        name="Axis",
        items=(
            ('X', "X", "X Axis"),
            ('Y', "Y", "Y Axis"),
            ('Z', "Z", "Z Axis"),
        ),
        description="Choose an axis for alignment",
        default='X'
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == "MESH" and context.active_object.mode == 'EDIT'

    def execute(self, context):
        values = {
            'X': [(0, 1, 1), (True, False, False)],
            'Y': [(1, 0, 1), (False, True, False)],
            'Z': [(1, 1, 0), (False, False, True)],
        }
        chosen_value = values[self.axis][0]
        constraint_value = values[self.axis][1]
        bpy.ops.transform.resize(
            value=chosen_value,
            constraint_axis=constraint_value,
            orient_type='GLOBAL',
            mirror=False,
            use_proportional_edit=False,
        )
        return {'FINISHED'}


class AlignAxisMinMaxOperator(Operator):
    bl_idname = "align.axis_minmax"
    bl_label = "Align to Front/Back Axis"
    bl_description = "Align to a Front or Back along the chosen Axis"
    bl_options = {'REGISTER', 'UNDO'}

    axis: EnumProperty(
        name="Axis",
        items=(
            ('X', "X", "X Axis"),
            ('Y', "Y", "Y Axis"),
            ('Z', "Z", "Z Axis"),
        ),
        description="Choose an axis for alignment",
        default='X'
    )
    side: EnumProperty(
        name="Side",
        items=[
            ('POSITIVE', "Front", "Align on the positive chosen axis"),
            ('NEGATIVE', "Back", "Align acriss the negative chosen axis"),
        ],
        description="Choose a side for alignment",
        default='POSITIVE'
    )

    def axis_str_to_int(self, axis_str: str) -> int:
        if axis_str == 'X':
            return 0
        elif axis_str == 'Y':
            return 1
        elif axis_str == 'Z':
            return 2
        else:
            raise Exception(f"Invalid Axis ({axis_str})")

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == "MESH" and context.active_object.mode == 'EDIT'

    def execute(self, context):

        bpy.ops.object.mode_set(mode='OBJECT')
        count = 0
        axe: int = self.axis_str_to_int(self.axis)
        for vert in bpy.context.object.data.vertices:
            if vert.select:
                if count == 0:
                    maxv = vert.co[axe]
                    count += 1
                    continue
                count += 1
                if self.side == 'POSITIVE':
                    if vert.co[axe] > maxv:
                        maxv = vert.co[axe]
                else:
                    if vert.co[axe] < maxv:
                        maxv = vert.co[axe]

        bpy.ops.object.mode_set(mode='OBJECT')

        for vert in bpy.context.object.data.vertices:
            if vert.select:
                vert.co[axe] = maxv
        bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}
