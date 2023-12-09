from bpy.types import Menu

from ..operators.view3d import SwitchModeOperator


class MainPieMenu(Menu):
    bl_idname = "OB_MT_Pie"
    bl_label = "OB"

    def draw(self, context):
        layout = self.layout
        ob = context.active_object
        pie = layout.menu_pie()
        scene = context.scene
        rd = scene.render
        tool_settings = context.tool_settings
        layout.scale_x = 2.0
        layout.scale_y = 1.75

        # Left
        left_box = pie.split().box().column()
        left_row = left_box.row(align=True)
        left_row.scale_x = 2
        left_box.operator(SwitchModeOperator.bl_idname, text='Vertex', icon='NONE').selection = 'VERT'

        # Right
        right_box = pie.split().box().column()
        right_row = right_box.row(align=True)

        # Bottom
        bottom_box = pie.split().box().column()
        bottom_row = bottom_box.row(align=True)
        bottom_row.operator(SwitchModeOperator.bl_idname, text='Face', icon='NONE').selection = 'FACE'

        # Top
        top_box = pie.split().box().column()
        top_row = top_box.row(align=True)
        top_row.operator(SwitchModeOperator.bl_idname, text='Edge', icon='NONE').selection = 'EDGE'

        # Top-Left
        top_left_box = pie.split().box().column()
        top_left_row = top_left_box.row(align=True)

        # Top-Right
        top_right_box = pie.split().box().column()
        top_right_row = top_right_box.row(align=True)
        top_right_row.operator('object.mode_set', text='Object', icon='NONE').mode = 'OBJECT'

        # Bottom-Left
        bottom_left_box = pie.split().box().column()
        bottom_left_row = bottom_left_box.row(align=True)

        # Bottom-Right
        bottom_right_box = pie.split().box().column()
        bottom_right_row = bottom_right_box.row(align=True)
        # bottom_right_row.prop(tool_settings, "use_snap", text="Snap")
