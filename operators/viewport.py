from bpy.props import EnumProperty
from bpy.types import Operator


class ToggleViewportCavity(Operator):
    """뷰포트의 Cavity를 토글합니다.
    """
    bl_idname = "view3d.toggle_viewport_cavity"
    bl_label = "Toggle Viewport Cavity"

    @classmethod
    def poll(cls, context):
        if context.area.spaces.active:
            return True
        else:
            return False

    def execute(self, context):
        space = context.area.spaces.active
        overlay = space.overlay
        shading = space.shading
        if not shading.show_cavity:
            shading.show_cavity = True
            shading.cavity_type = "BOTH"  # ["SCREEN", "WORLD"]
            shading.cavity_ridge_factor = 1.0
            shading.cavity_valley_factor = 1.0
            shading.curvature_ridge_factor = 1.0
            shading.curvature_valley_factor = 1.0
        else:
            shading.show_cavity = False
        return {"FINISHED"}


class ToggleViewportCamera(Operator):
    """Perspective와 활성화된 카메라 사이를 토글한다.

    카메라를 선택한 뒤 실행하면 Active카메라로 지정하고
    Perspective 모드인 경우 Camera모드로 토글한다. Camera모드인 상태에서 실행하면 Perspective 모드로 토글된다.
    카메라를 선택하지 않은 상태에서 실행하면 마지막으로 Active된 카메라로 토글된다.
    """
    bl_idname = "view3d.toggle_viewport_camera_operator"
    bl_label = "Toggle Viewport Camera Operator"

    @classmethod
    def poll(cls, context):
        return context.area.type == "VIEW_3D"

    def execute(self, context):
        area = context.area
        space = context.area.spaces.active
        region_3d = space.region_3d

        # 1) 현재 선택된 오브젝트가 카메라인 경우 Active Camera로 지정한다.
        selected_cameras = [obj for obj in context.selected_objects if obj.type == "CAMERA"]
        if len(selected_cameras) > 0:
            selected_camera = selected_cameras[0]
            print(f"액티브 카메라 지정: {selected_camera}")
            context.scene.camera = selected_camera

        # 2) PERSP <=> CAMERA 뷰로 토글
        active_camera = context.scene.camera
        current_view_perspective = region_3d.view_perspective
        current_lock_camera_to_view = space.lock_camera

        if region_3d.view_perspective == "PERSP":
            # print(f"카메라로 보기: {active_camera}")
            space.lock_camera = True
            region_3d.view_perspective = "CAMERA"
        elif region_3d.view_perspective == "CAMERA":
            space.lock_camera = False
            region_3d.view_perspective = "PERSP"

        else:
            return {'CANCELLED'}
        return {'FINISHED'}


class SetViewportLightingMode(Operator):
    """뷰포트의 모드를 변경합니다.
    """
    bl_idname = "view3d.set_viewport_lighting_mode"
    bl_label = "Set Viewport Lighting Mode"

    mode: EnumProperty(
        name="LightingMode",
        items=(
            ("DEFAULT", "Default", "Default Lighting"),
            ("SCULPT", "Sculpt", "Sculpt Lighting"),
        )
    )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        space = context.area.spaces.active
        overlay = space.overlay
        shading = space.shading
        current_mode: str = str(self.mode)
        if current_mode == "DEFAULT":
            shading.light = "STUDIO"
            shading.studio_light = "Default"
        elif current_mode == "SCULPT":
            shading.light = "MATCAP"
            shading.studio_light = "clay_brown.exr"
        else:
            return {'CANCELLED'}
        return {'FINISHED'}
