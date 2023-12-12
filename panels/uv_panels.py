from bpy.types import Panel

from ..functions.context import is_mode
from ..functions.ui import create_gridflow_at_layout


class UVSidePanelBase:
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "UI"
    bl_category = "OB"
    bl_options = {"DEFAULT_CLOSED"}


class UVEditPanel(UVSidePanelBase, Panel):
    bl_idname = "OB_PT_UVEditPanel"
    bl_label = "UV Edit"

    def draw(self, context):
        tool_settings = context.tool_settings

        if is_mode("EDIT_MESH"):
            settings_grid = create_gridflow_at_layout(self.layout, columns=1)
            settings_grid.prop(tool_settings, "use_uv_select_sync", text="Sync Selection")

        edit_grid = create_gridflow_at_layout(self.layout, columns=2, header_text="")
        edit_grid.operator("uv.weld", text="Weld")

        edit_grid.operator("uv.select_split", text="Split")
        edit_grid.operator("uv.stitch", text="Stitch")

        unwrap_grid = create_gridflow_at_layout(self.layout, columns=2, header_text="")
        unwrap_grid.operator("uv.pin", text="Pin").clear = False
        unwrap_grid.operator("uv.pin", text="Unpin").clear = True
        unwrap_grid.operator("uv.unwrap", text="Unwrap")
        # unwrap_grid.label()

        align_grid = create_gridflow_at_layout(self.layout, columns=2, header_text="")
        align_grid.operator("uv.align", text="Align Axis").axis = "ALIGN_AUTO"
        align_grid.operator("uv.align_rotation", text="Align Rotation")
        align_grid.operator("uv.align", text="Align X").axis = "ALIGN_X"
        align_grid.operator("uv.align", text="Align Y").axis = "ALIGN_Y"

        if is_mode("EDIT_MESH"):
            mirror_x_op = align_grid.operator("transform.mirror", text="Mirror X")
            mirror_x_op.constraint_axis = (True, False, False)
            mirror_x_op.release_confirm = True
            mirror_y_op = align_grid.operator("transform.mirror", text="Mirror Y")
            mirror_y_op.constraint_axis = (False, True, False)
            mirror_y_op.release_confirm = True

        island_grid = create_gridflow_at_layout(self.layout, columns=2, header_text="Island")
        island_grid.operator("uv.average_islands_scale", text="Scale Average")
        island_grid.operator("uv.pack_islands", text="Pack Islands")

        projection_grid = create_gridflow_at_layout(self.layout, columns=2, header_text="Projection")
        projection_grid.operator("uv.smart_project", text="Smart")
        projection_grid.operator("uv.cube_project", text="Cube")
        projection_grid.operator("uv.cylinder_project", text="Cylinder")
        projection_grid.operator("uv.sphere_project", text="Sphere")

        data_grid = create_gridflow_at_layout(self.layout, columns=1, header_text="Data")
        data_grid.operator("uv.seams_from_islands", text="Set Seams From Islands")
