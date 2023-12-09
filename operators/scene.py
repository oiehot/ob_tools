from bpy.types import Operator

from ..functions.debug import print_all
from ..functions.optimization import fix_data_names


class PrintAllHierarchy(Operator):
    bl_idname = "scene.print_all_hierarchy"
    bl_label = "Print All Hierarchy"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        print_all()
        return {'FINISHED'}


class FixMeshNames(Operator):
    bl_idname = "scene.fix_mesh_names"
    bl_label = "Fix Mesh Names"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        fix_data_names()
        cmpl_msg: str = "Data objects names modification completed."  # "오브젝트 데이터 노드들의 이름을 정리했습니다."
        self.report({'INFO'}, cmpl_msg)
        return {'FINISHED'}
