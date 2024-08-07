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


class FixDataNames(Operator):
    bl_idname = "scene.fix_data_names"
    bl_label = "Fix Data Names"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        fix_data_names()
        self.report({'INFO'}, "Data names modification completed.")
        return {'FINISHED'}
