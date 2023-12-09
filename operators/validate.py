from bpy.types import Operator

from ..functions.validate import (
    get_objects_issues,
    get_collection_issues,
    get_material_issues,
    print_issues
)


class ValidateScene(Operator):
    bl_idname = "validate.validate_scene"
    bl_label = "Validate Scene"
    TEXTBLOCK_NAME = "TXT_ValidateResult"

    def execute(self, context):
        issues = []
        issues.extend(get_objects_issues())
        issues.extend(get_collection_issues())
        issues.extend(get_material_issues())
        print_issues(issues)
        return {"FINISHED"}
