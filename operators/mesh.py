import bpy
from bpy.props import FloatProperty
from bpy.types import Operator

from ..functions.context import get_mode, set_mode
from ..functions.context import is_edit_mode, is_component_selected


class QuickMeshDeleteOperator(Operator):
    bl_idname = "mesh.quick_mesh_delete"
    bl_label = "Quick Mesh Delete"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if is_edit_mode() and is_component_selected():
            return True
        else:
            return False

    def execute(self, context):
        mode: tuple = bpy.context.tool_settings.mesh_select_mode[:]
        if mode[0]:  # Vertex
            bpy.ops.mesh.dissolve_verts()
        elif mode[1]:  # Edge
            bpy.ops.mesh.dissolve_edges()
        elif mode[2]:  # Face
            bpy.ops.mesh.delete(type='FACE')
        else:
            return {'CANCELLED'}
        return {'FINISHED'}


class MergeCloseVertices(Operator):
    """가까운 Vertex들을 병합시킨다.
    """
    bl_idname = "mesh.merge_close_vertices"
    bl_label = "Merge Close Vertices"
    bl_options = {"REGISTER", "UNDO"}

    merge_threshold: FloatProperty(
        name="Merge Threshold",
        description="Maximum distance between vertices to merge",
        default=0.001,
        min=0.001,
        max=1.0
    )

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == "MESH"

    def execute(self, context):
        previous_mode: str = get_mode()
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.remove_doubles(threshold=self.merge_threshold)
        set_mode(previous_mode)
        return {"FINISHED"}


class SelectBoundaryEdges(Operator):
    """가까운 Vertex들을 병합시킨다.
    """
    bl_idname = "mesh.select_boundary_edges"
    bl_label = "Select Boundary Edges"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == "MESH"

    def execute(self, context):
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.region_to_loop()
        return {"FINISHED"}
