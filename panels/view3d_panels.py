from collections import namedtuple

import bpy
from bpy.types import Panel

from ..functions.context import is_mode, get_active_object_by_type, is_object_mode, has_selected_objects
from ..functions.gpencil import is_current_grease_pencil_brush_name, is_grease_pencil_placement_mode, \
    get_active_material_in_gpencil_object
from ..functions.ui import create_gridflow_at_layout
from ..operators.align import AlignAxisAverageOperator, AlignAxisMinMaxOperator
from ..operators.armature import ToggleWeightPaintMode
from ..operators.gpencil import SetStrokePlacement, SetBrushAndMaterial
from ..operators.material import ClearUnusedMaterials, CopyMaterial, PasteMaterial, CreateAndAssignMaterial
from ..operators.mesh import MergeCloseVertices, QuickMeshDeleteOperator, SelectBoundaryEdges
from ..operators.modifier import CreateQuickLattice, ApplyQuickLattice, RemoveQuickLattice
from ..operators.rigging import (
    GenerateRigFromArmature, RemoveGeneratedRig,
    AutoSkin,
    DetachRigMesh, AttachRigMesh,
    SaveObjectVertexGroups, LoadObjectVertexGroups
)
from ..operators.scene import FixMeshNames, PrintAllHierarchy
from ..operators.text import CreateText
from ..operators.validate import ValidateScene
from ..operators.viewport import SetViewportLightingMode, ToggleViewportCamera, ToggleViewportCavity
from ..operators.render import SetRenderSettings, ExploreRenderOutputPath
from ..utils import is_developer_mode

MaterialInfo = namedtuple("GPencilMaterialInfo", "show_stroke show_fill stroke_color fill_color")
ToolInfo = namedtuple("GPencilTemplateInfo", "brush_name material_name")

GREASE_PENCIL_BRUSHES = [
    "Pencil",
    "Pencil Soft",
    "Ink Pen",
    "Ink Pen Rough",
    # "Marker Bold",
    "Marker Chisel",
    # "Airbrush",
]

GREASE_PENCIL_ERASERS = [
    # "Eraser Hard",
    # "Eraser Soft",
    "Eraser Point",
    "Eraser Stroke",
]

GREASE_PENCIL_PLACEMENTS = [
    "ORIGIN",
    "SURFACE",
    "CURSOR",
    "STROKE",
]

GREASE_PENCIL_MATERIAL_INFOS = {
    "GPM_Red": MaterialInfo(True, False, (1, 0, 0, 1), (1, 1, 1, 1)),
    "GPM_Green": MaterialInfo(True, False, (0, 1, 0, 1), (1, 1, 1, 1)),
    "GPM_Blue": MaterialInfo(True, False, (0, 0, 1, 1), (1, 1, 1, 1)),
    "GPM_Black": MaterialInfo(True, False, (0, 0, 0, 1), (1, 1, 1, 1)),
    "GPM_White": MaterialInfo(True, False, (1, 1, 1, 1), (0, 0, 0, 1)),
}

GREASE_PENCIL_TOOL_INFOS = {
    "Pencil": ToolInfo("Pencil", "GPM_Black"),
    "Airbrush": ToolInfo("Pencil Soft", "GPM_Black"),
    "Red Pen": ToolInfo("Ink Pen", "GPM_Red"),
    "Green Pen": ToolInfo("Ink Pen", "GPM_Green"),
    "Blue Pen": ToolInfo("Ink Pen", "GPM_Blue"),
    "Black Pen": ToolInfo("Ink Pen", "GPM_Black"),
    "White Pen": ToolInfo("Ink Pen", "GPM_White"),
}


class View3DSidePanelBase:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "OB"
    bl_options = {"DEFAULT_CLOSED"}


# class SelectionPanel(SidePanelBase, Panel):
#     bl_idname = "OB_PT_SelectionPanel"
#     bl_label = "Selection"
#     # bl_parent_id = MainPanel.bl_idname
#
#     @classmethod
#     def poll(cls, context):
#         return False
#
#     def draw(self, context):
#         selection_grid = _get_gridflow(self.layout, columns=3)
#         selection_grid.operator(SwitchModeOperator.bl_idname, text='Vertex', icon='NONE').selection = 'VERT'
#         selection_grid.operator(SwitchModeOperator.bl_idname, text='Edge', icon='NONE').selection = 'EDGE'
#         selection_grid.operator(SwitchModeOperator.bl_idname, text='Face', icon='NONE').selection = 'FACE'
#         selection_grid.operator('object.mode_set', text='Object', icon='NONE').mode='OBJECT'


class ViewPanel(View3DSidePanelBase, Panel):
    bl_idname = "OB_PT_ViewPanel"
    bl_label = "View & Camera"

    def _is_xray(self, context) -> bool:
        shading = context.area.spaces.active.shading
        if shading.type == "WIREFRAME":
            return shading.show_xray_wireframe
        else:
            return shading.show_xray

    def _is_cavity(self, context) -> bool:
        shading = context.area.spaces.active.shading
        return shading.show_cavity

    def _is_default_lighting(self, context) -> bool:
        shading = context.area.spaces.active.shading
        return True if shading.light == "STUDIO" and shading.studio_light == "Default" else False

    def _is_sculpt_lighting(self, context) -> bool:
        shading = context.area.spaces.active.shading
        return True if shading.light == "MATCAP" and shading.studio_light == "clay_brown.exr" else False

    def _is_local_view(self, context) -> bool:
        return context.space_data.local_view is not None

    def _is_camera_view(self, context) -> bool:
        return context.area.spaces.active.region_3d.view_perspective == "CAMERA"

    def _is_quad_view(self, context) -> bool:
        space_data = context.space_data
        if space_data.type == 'VIEW_3D':
            return space_data.region_quadviews is not None and len(space_data.region_quadviews) > 0
        return False

    def draw(self, context):
        space = context.area.spaces.active
        # overlay = context.space_data.overlay
        overlay = space.overlay
        shading = space.shading

        axis_grid = create_gridflow_at_layout(self.layout, columns=4)
        axis_grid.operator('view3d.view_axis', text='Top', icon='NONE').type = 'TOP'
        axis_grid.operator('view3d.view_axis', text='Left', icon='NONE').type = 'LEFT'
        axis_grid.operator('view3d.view_axis', text='Right', icon='NONE').type = 'RIGHT'
        axis_grid.operator('view3d.view_axis', text='Front', icon='NONE').type = 'FRONT'
        axis_grid.operator('screen.region_quadview', text='Quad', depress=self._is_quad_view(context))
        axis_grid.operator(ToggleViewportCamera.bl_idname, text='Camera', depress=self._is_camera_view(context))
        axis_grid.operator('view3d.localview', text='Isolate', depress=self._is_local_view(context))

        viewport_grid = create_gridflow_at_layout(self.layout, columns=3)
        viewport_grid.operator('view3d.toggle_xray', text="XRay", depress=self._is_xray(context))
        viewport_grid.prop(overlay, "show_wireframes", text="Wire", toggle=True)
        viewport_grid.operator(ToggleViewportCavity.bl_idname, text="Cavity", depress=self._is_cavity(context))
        viewport_grid.prop(overlay, "show_edge_crease", text="Crease", toggle=True)
        viewport_grid.prop(overlay, "show_edge_sharp", text="Sharp", toggle=True)
        viewport_grid.prop(overlay, "show_edge_bevel_weight", text="Bevel", toggle=True)
        viewport_grid.prop(overlay, "show_edge_seams", text="Seams", toggle=True)
        viewport_grid.prop(shading, "show_backface_culling", text="BackCull", toggle=True)
        viewport_grid.prop(overlay, "show_face_orientation", text="Orient", toggle=True)

        lighting_grid = create_gridflow_at_layout(self.layout, columns=3)
        lighting_grid.operator(SetViewportLightingMode.bl_idname, text="Default Lit",
                               depress=self._is_default_lighting(context)).mode = "DEFAULT"
        lighting_grid.operator(SetViewportLightingMode.bl_idname, text="Sculpt Lit",
                               depress=self._is_sculpt_lighting(context)).mode = "SCULPT"


# class SnapPanel(SidePanelBase, Panel):
#     bl_idname = "OB_PT_SnapPanel"
#     # bl_parent_id = MainPanel.bl_idname
#     bl_label = "Snap"
#
#     @classmethod
#     def poll(cls, context):
#         return False
#
#     def draw(self, context):
#         active_object = context.active_object
#         object_mode = 'OBJECT' if active_object is None else active_object.mode
#         tool_settings = context.tool_settings
#         box = self.layout.column()
#         box.scale_y = DEFAULT_SCALE_Y
#
#         ## Snap
#         snap_row = box.row(align=True)
#         snap_row.prop(tool_settings, "use_snap", text="Snap")
#         snap_to_text:str = ""
#         snap_elements:list[str] = list(tool_settings.snap_elements)
#         if len(snap_elements) <= 0:
#             snap_to_text = "None"
#         elif len(snap_elements) == 1:
#             snap_to_text = snap_elements[0].capitalize()
#         else:
#             snap_to_text = "Mix"
#         snap_row.popover(
#             panel="VIEW3D_PT_snapping",
#             icon="NONE",
#             text=snap_to_text,
#         )
#
#         ## Orientation
#         orientation_row = box.row(align=True)
#         orientation_row.prop_with_popover(
#             bpy.context.scene.transform_orientation_slots[0],
#             "type",
#             text="",
#             panel="VIEW3D_PT_transform_orientations",
#         )
#
# Transform Pivot Point
#         pivot_row = box.row(align=True)
#         if object_mode in {'OBJECT', 'EDIT', 'EDIT_GPENCIL', 'SCULPT_GPENCIL'} or has_pose_mode:
#             pivot_row.prop(tool_settings, "transform_pivot_point", text="", icon_only=False)


class CreatePanel(View3DSidePanelBase, Panel):
    bl_idname = "OB_PT_CreatePanel"
    # bl_parent_id = MainPanel.bl_idname
    bl_label = "Create"

    def draw(self, context):
        primitive_grid = create_gridflow_at_layout(self.layout, columns=3)
        primitive_grid.operator("mesh.primitive_cube_add", text="Cube", icon="NONE")
        primitive_grid.operator("mesh.primitive_uv_sphere_add", text="Sphere", icon="NONE")
        primitive_grid.operator("mesh.primitive_cylinder_add", text="Cylinder", icon="NONE")
        primitive_grid.operator("mesh.primitive_plane_add", text="Plane", icon="NONE")
        primitive_grid.operator("mesh.primitive_grid_add", text="Grid", icon="NONE")
        primitive_grid.operator("mesh.primitive_torus_add", text="Torus", icon="NONE")

        etc_grid = create_gridflow_at_layout(self.layout, columns=2)
        etc_grid.operator(CreateText.bl_idname, text="Text").text = "Hello, World!"

        # meta_grid = _get_gridflow(self.layout, columns=3, header_text="Meta")
        # meta_grid.operator("object.metaball_add", text="Ball", icon="NONE").type = "BALL"
        # meta_grid.operator("object.metaball_add", text="Cube", icon="NONE").type = "CUBE"
        # meta_grid.operator("object.metaball_add", text="Capsule", icon="NONE").type = "CAPSULE"
        # meta_grid.operator("object.metaball_add", text="Plane", icon="NONE").type = "PLANE"
        # meta_grid.operator("object.metaball_add", text="Ellipsoid", icon="NONE").type = "ELLIPSOID" # 타원체


class EditPanel(View3DSidePanelBase, Panel):
    bl_idname = "OB_PT_EditPanel"
    # bl_parent_id = MainPanel.bl_idname
    bl_label = "Edit"

    def draw(self, context):
        # Origin & 3D Cursor
        origin_grid = create_gridflow_at_layout(self.layout, columns=2, header_text="")
        origin_grid.prop(bpy.context.scene.tool_settings, "use_transform_data_origin", text="Edit Pivot", toggle=True)
        origin_grid.label()
        # origin_grid.operator('object.move_to_collection', text="Group (M)")
        origin_grid.operator('object.parent_set', text="Parent").type = "OBJECT"
        origin_grid.operator('object.parent_clear', text="Unparent").type = "CLEAR_KEEP_TRANSFORM"  # "CLEAR"

        deform_grid = create_gridflow_at_layout(self.layout, columns=2)
        deform_grid.operator(CreateQuickLattice.bl_idname, text="Lattice Local").orientation = "LOCAL"
        deform_grid.operator(CreateQuickLattice.bl_idname, text="Lattice Normal").orientation = "NORMAL"
        deform_grid.operator(ApplyQuickLattice.bl_idname, text="Apply Lattice")
        deform_grid.operator(RemoveQuickLattice.bl_idname, text="Remove Lattice")
        scale_cage_op = deform_grid.operator("wm.tool_set_by_id", text="Scale Cage")
        scale_cage_op.name = "builtin.scale_cage"
        scale_cage_op.cycle = True

        # Object Tools
        object_grid = create_gridflow_at_layout(self.layout, columns=2, header_text="")
        object_grid.enabled = is_object_mode() and has_selected_objects()
        object_grid.operator('object.join', text='Join')
        object_grid.operator('mesh.separate', text='Separate').type = 'LOOSE'
        object_grid.operator('object.origin_set', text='Center Pivot').type = 'ORIGIN_GEOMETRY'
        # object_grid.operator('object.reset_origin_position', text='Reset Pivot')
        object_grid.operator('object.transforms_to_deltas', text='Freeze', icon='NONE').mode = 'ALL'

        # Common Tools
        common_grid = create_gridflow_at_layout(self.layout, columns=2, header_text="")
        common_grid.operator('mesh.merge', text='Merge', icon='NONE').type = 'CENTER'
        common_grid.operator(MergeCloseVertices.bl_idname, text='Merge Near', icon='NONE')
        common_grid.operator('mesh.split', text='Extract', icon='NONE')
        common_grid.operator(QuickMeshDeleteOperator.bl_idname, text='Delete', icon='NONE')
        common_grid.operator('view3d.edit_mesh_extrude_move_normal', text="Extrude",
                             icon='NONE')  # Ctrl+RMB 로 커브형 Extrude 가능함.
        common_grid.operator('mesh.edge_face_add', text="Fill")

        # Vertex Tools
        vertex_grid = create_gridflow_at_layout(self.layout, header_text="")
        vertex_grid.operator('mesh.vert_connect_path', text='V ConnectPath', icon='NONE')

        # Edge Tools
        edge_grid = create_gridflow_at_layout(self.layout, header_text="")
        edge_grid.operator('mesh.bevel', text='E Bevel', icon='NONE').affect = 'EDGES'
        edge_grid.operator('transform.edge_slide', text='E Slide', icon='NONE')
        edge_grid.operator('mesh.loopcut_slide', text='E /', icon='NONE')
        edge_grid.operator('mesh.offset_edge_loops_slide', text="E //", icon='NONE')
        edge_grid.operator('mesh.knife_tool', text="E Knife", icon='NONE')
        edge_grid.operator("mesh.rip", text="E Rip")

        # Face Tools
        face_grid = create_gridflow_at_layout(self.layout, header_text="")
        face_grid.operator('mesh.inset', text="F Inset", icon='NONE')
        face_grid.operator('mesh.subdivide', text='F Subdivde', icon='NONE')
        face_grid.operator('mesh.unsubdivide', text='F Unsubdive', icon='NONE')
        face_separate = face_grid.operator('mesh.separate', text='F Separate', icon='NONE')
        face_separate.type = 'SELECTED'
        # face_separate.enabled = is_edit_mode()

        # Vertex Alignment
        VA_EMBOSS: bool = False
        va_grid = create_gridflow_at_layout(self.layout, header_text="")
        x_max = va_grid.operator(AlignAxisMinMaxOperator.bl_idname, text='+', icon='NONE', emboss=VA_EMBOSS)
        x_max.axis = 'X'
        x_max.side = 'POSITIVE'
        y_max = va_grid.operator(AlignAxisMinMaxOperator.bl_idname, text='+', icon='NONE', emboss=VA_EMBOSS)
        y_max.axis = 'Y'
        y_max.side = 'POSITIVE'
        z_max = va_grid.operator(AlignAxisMinMaxOperator.bl_idname, text='+', icon='NONE', emboss=VA_EMBOSS)
        z_max.axis = 'Z'
        z_max.side = 'POSITIVE'
        va_grid.operator(AlignAxisAverageOperator.bl_idname, text='X', icon='NONE').axis = 'X'
        va_grid.operator(AlignAxisAverageOperator.bl_idname, text='Y', icon='NONE').axis = 'Y'
        va_grid.operator(AlignAxisAverageOperator.bl_idname, text='Z Up', icon='NONE').axis = 'Z'
        x_min = va_grid.operator(AlignAxisMinMaxOperator.bl_idname, text='-', icon='NONE', emboss=VA_EMBOSS)
        x_min.axis = 'X'
        x_min.side = 'NEGATIVE'
        y_min = va_grid.operator(AlignAxisMinMaxOperator.bl_idname, text='-', icon='NONE', emboss=VA_EMBOSS)
        y_min.axis = 'Y'
        y_min.side = 'NEGATIVE'
        z_min = va_grid.operator(AlignAxisMinMaxOperator.bl_idname, text='-', icon='NONE', emboss=VA_EMBOSS)
        z_min.axis = 'Z'
        z_min.side = 'NEGATIVE'

        # Selection Tools
        selection_grid = create_gridflow_at_layout(self.layout, header_text="")
        selection_grid.operator("mesh.select_linked", text="SEL Linked")
        selection_grid.operator(SelectBoundaryEdges.bl_idname, text="SEL Boundary")


class Riggingpanel(View3DSidePanelBase, Panel):
    bl_idname = "OB_PT_RiggingPanel"
    bl_label = "Rigging"

    def draw(self, context):
        armature_grid = create_gridflow_at_layout(self.layout, columns=2, header_text="Armature")
        armature_grid.operator("object.armature_add", text="Create Armature")
        armature_grid.operator("object.armature_basic_human_metarig_add", text="Basic Human")
        armature_grid.operator("object.armature_human_metarig_add", text="Full Human")
        armature_grid.label()

        # rigging_grid.operator("pose.rigify_generate", text="Generate Rig")
        armature_grid.operator(GenerateRigFromArmature.bl_idname, text="Generate Rig")
        armature_grid.operator(RemoveGeneratedRig.bl_idname, text="Remove Rig")
        armature_grid.operator(AttachRigMesh.bl_idname, text="Attach Mesh")
        armature_grid.operator(DetachRigMesh.bl_idname, text="Detach Mesh")
        armature_grid.operator(AutoSkin.bl_idname, text="Auto Skin")
        armature_grid.operator("pose.transforms_clear", text="Reset Pose")

        weight_paint_grid = create_gridflow_at_layout(self.layout, columns=2, header_text="Weight Paint")
        weight_paint_grid.operator_context = "EXEC_DEFAULT"  # Save, Load시 invoke 메서드를 호출시키지 않기 위해
        weight_paint_grid.operator(ToggleWeightPaintMode.bl_idname, text="Edit Weight Mode")
        weight_paint_grid.label()
        clean_vg = weight_paint_grid.operator("object.vertex_group_clean", text="Cleanup")
        clean_vg.group_select_mode = "ACTIVE"
        clean_vg.limit = 0.05
        weight_paint_grid.prop(bpy.data.brushes["Draw"], "use_frontface", text="Front Face Only", toggle=True)

        vertex_group_grid = create_gridflow_at_layout(self.layout, columns=2, header_text="Vertex Group")
        vertex_group_grid.operator_context = "INVOKE_DEFAULT"  # 개별 Operator에서는 operator_context를 사용할 수 없었음.
        vertex_group_grid.operator(SaveObjectVertexGroups.bl_idname, text="Save")
        vertex_group_grid.operator(LoadObjectVertexGroups.bl_idname, text="Load")


class NormalPanel(View3DSidePanelBase, Panel):
    bl_idname = "OB_PT_NormalPanel"
    bl_label = "Normal"

    def draw(self, context):
        normal_tool_grid = create_gridflow_at_layout(self.layout, columns=2)
        normal_tool_grid.operator("mesh.mark_sharp", text="Mark Sharp")
        normal_tool_grid.operator("mesh.mark_sharp", text="Clear Sharp").clear = True
        normal_tool_grid.operator("mesh.flip_normals", text="Reverse", icon="NONE")


class UVPanel(View3DSidePanelBase, Panel):
    bl_idname = "OB_PT_UVPanel"
    bl_label = "UV"

    def draw(self, context):
        uv_grid = create_gridflow_at_layout(self.layout, columns=3)
        uv_grid.operator("mesh.mark_seam", text="Mark Seam").clear = False
        uv_grid.operator("mesh.mark_seam", text="Clear Seam").clear = True


class GreasePencilPanel(View3DSidePanelBase, Panel):
    bl_idname = "OB_PT_GreasePencilPanel"
    bl_label = "Grease Pencil"

    def draw(self, context):
        gpencil_object: Object | None = get_active_object_by_type("GPENCIL")

        gpencil_grid = create_gridflow_at_layout(self.layout, columns=2)
        gpencil_grid.operator("object.gpencil_add", text="+").type = "EMPTY"
        gpencil_grid.label()
        gpencil_grid.operator("object.mode_set", text="Object Mode", depress=is_mode("OBJECT")).mode = "OBJECT"

        if gpencil_object:
            try:
                gpencil_grid.operator("object.mode_set", text="Draw Mode",
                                      depress=is_mode("PAINT_GPENCIL")).mode = "PAINT_GPENCIL"
            except:
                pass

        # Placement
        placement_grid = create_gridflow_at_layout(self.layout, columns=2, header_text="Placement")
        for mode in GREASE_PENCIL_PLACEMENTS:
            placement_grid.operator(SetStrokePlacement.bl_idname, text=f"On {mode.capitalize()}",
                                    depress=is_grease_pencil_placement_mode(mode)).placement = mode

        # Brush
        brushes_grid = create_gridflow_at_layout(self.layout, columns=2, header_text="Brush")
        for brush_name in GREASE_PENCIL_BRUSHES:
            op = brushes_grid.operator(SetBrushAndMaterial.bl_idname, text=brush_name,
                                       depress=is_current_grease_pencil_brush_name(brush_name))
            op.set_brush = True
            op.brush_name = brush_name

        # Eraser
        eraser_grid = create_gridflow_at_layout(self.layout, columns=2, header_text="Eraser")
        for eraser_name in GREASE_PENCIL_ERASERS:
            op = eraser_grid.operator(SetBrushAndMaterial.bl_idname, text=eraser_name,
                                      depress=is_current_grease_pencil_brush_name(eraser_name))
            op.set_brush = True
            op.brush_name = eraser_name

        # Material
        active_material: Material | None = get_active_material_in_gpencil_object(gpencil_object)
        material_grid = create_gridflow_at_layout(self.layout, columns=2, header_text="Material")
        for material_name, info in GREASE_PENCIL_MATERIAL_INFOS.items():
            button_text = material_name.split("_")[-1]
            op = material_grid.operator(SetBrushAndMaterial.bl_idname, text=button_text,
                                        depress=True if active_material and active_material.name == material_name else False)
            op.set_material = True
            op.material_name = material_name
            op.show_stroke = info.show_stroke
            op.show_fill = info.show_fill
            op.stroke_color = info.stroke_color
            op.fill_color = info.fill_color

        # tool_grid = _get_gridflow(self.layout, columns=2, header_text="Toolsets")
        # for tool_name, tool_info in GREASE_PENCIL_TOOL_INFOS.items():
        #     brush_name: str = tool_info.brush_name
        #     material_name: str = tool_info.material_name
        #     material_info = GREASE_PENCIL_MATERIAL_INFOS[material_name]
        #     op = tool_grid.operator(SetBrushAndMaterial.bl_idname, text=tool_name)
        #     op.set_brush = True
        #     op.set_material = True
        #     op.brush_name = brush_name
        #     op.material_name = material_name
        #     op.show_stroke = material_info.show_stroke
        #     op.show_fill = material_info.show_fill
        #     op.stroke_color = material_info.stroke_color
        #     op.fill_color = material_info.fill_color

        # TODO: Overlap Stroke Option for airbrush
        # blue_marker.use_overlap_stroke = True


class LookPanel(View3DSidePanelBase, Panel):
    bl_idname = "OB_PT_LookPanel"
    bl_label = "Look"

    def draw(self, context):
        light_grid = create_gridflow_at_layout(self.layout, columns=4, header_text=None)
        light_grid.operator("object.light_add", text="Sun", icon="NONE").type = "SUN"
        light_grid.operator("object.light_add", text="Point", icon="NONE").type = "POINT"
        light_grid.operator("object.light_add", text="Spot", icon="NONE").type = "SPOT"
        light_grid.operator("object.light_add", text="Area", icon="NONE").type = "AREA"

        material_grid = create_gridflow_at_layout(self.layout, columns=2)
        material_grid.operator(CreateAndAssignMaterial.bl_idname, text="New Mat", icon="NONE").color = "RANDOM"
        material_grid.label(text="")
        material_grid.operator(CopyMaterial.bl_idname, text="Copy Mat", icon="NONE")
        material_grid.operator(PasteMaterial.bl_idname, text="Paste Mat", icon="NONE")

        palette_grid = create_gridflow_at_layout(self.layout, columns=3, header_text="")
        palette_grid.operator(CreateAndAssignMaterial.bl_idname, text="R").color = "RED"
        palette_grid.operator(CreateAndAssignMaterial.bl_idname, text="G").color = "GREEN"
        palette_grid.operator(CreateAndAssignMaterial.bl_idname, text="B").color = "BLUE"
        palette_grid.operator(CreateAndAssignMaterial.bl_idname, text="White").color = "WHITE"
        palette_grid.operator(CreateAndAssignMaterial.bl_idname, text="Gray").color = "GRAY"
        palette_grid.operator(CreateAndAssignMaterial.bl_idname, text="Black").color = "BLACK"
        palette_grid.operator(CreateAndAssignMaterial.bl_idname, text="Checker").color = "CHECKER"


class OptimizationPanel(View3DSidePanelBase, Panel):
    bl_idname = "OB_PT_OptimizationPanel"
    bl_label = "Optimization"

    def draw(self, context):
        optimization_grid = create_gridflow_at_layout(self.layout, columns=1)
        optimization_grid.operator(PrintAllHierarchy.bl_idname, text="Print Hierarchy")
        optimization_grid.operator(ValidateScene.bl_idname, text="Validate Scene")
        optimization_grid.operator(FixMeshNames.bl_idname, text="Fix Mesh Names")
        optimization_grid.operator(ClearUnusedMaterials.bl_idname, text="Cleanup Materials")
        optimization_grid.operator("outliner.orphans_purge", text="Cleanup Datablocks")


class RenderPanel(View3DSidePanelBase, Panel):
    bl_idname = "OB_PT_RenderPanel"
    bl_label = "Rendering"

    def draw(self, context):
        render_grid = create_gridflow_at_layout(self.layout, columns=3)
        render_grid.operator("render.render", text="Render Still").write_still=True
        render_grid.operator("render.render", text="Render Ani").animation=True
        render_settings_grid = create_gridflow_at_layout(self.layout, columns=1)
        render_settings_grid.operator(ExploreRenderOutputPath.bl_idname, text="Open Output Path")
        render_settings_grid.operator(SetRenderSettings.bl_idname, text="Set Default Settings").mode="DEFAULT"


class SystemPanel(View3DSidePanelBase, Panel):
    bl_idname = "OB_PT_SystemPanel"
    bl_label = "System"

    def draw(self, context):
        system_grid = create_gridflow_at_layout(self.layout, columns=2)
        system_grid.operator('object.mode_set', text='Object Mode', icon='NONE').mode = 'OBJECT'

        # Edit Mode
        try:
            system_grid.operator('object.mode_set', text='Edit Mode', icon='NONE').mode = 'EDIT'
        except:
            pass

        # Sculpt Mode
        try:
            system_grid.operator('object.mode_set', text='Sculpt Mode', icon='NONE').mode = 'SCULPT'
        except:
            pass

        # Pose Mode
        try:
            system_grid.operator("object.mode_set", text="Pose Mode").mode = "POSE"
        except:
            pass

        system_grid.operator('wm.console_toggle', text='Console', icon='NONE')

        if is_developer_mode():
            dev_grid = create_gridflow_at_layout(self.layout, columns=1)
            dev_grid.operator("script.reload", text="Refresh", icon="FILE_REFRESH")
