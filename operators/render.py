import os

from bpy.props import EnumProperty
from bpy.types import Operator

from ..utils.file import explore_path


class SetRenderSettings(Operator):
    """기본 혹은 특정 템플릿으로 렌더링 설정을 바꾼다.
    """
    bl_idname = "render.set_render_settings"
    bl_label = "Explore Output Path"

    mode: EnumProperty(
        name="Mode",
        items=(
            ("DEFAULT", "Default", "Default Render Settings"),
        ),
        default="DEFAULT"
    )

    @classmethod
    def poll(cls, context):
        scene = context.scene
        render = scene.render
        return True if scene and render else False

    def execute(self, context):
        scene = context.scene
        render = scene.render
        image_settings = render.image_settings

        match self.mode:
            case "DEFAULT":
                print("Set Default Render Settings")

                # Format
                render.resolution_x = 1920
                render.resolution_y = 1080
                render.pixel_aspect_x = 1
                render.pixel_aspect_y = 1
                render.resolution_percentage = 100
                render.use_border = False
                render.use_multiview = False  # Stereoscopy

                # Output
                # render.filepath = "d:/tmp/test_####"
                render.use_file_extension = True
                render.use_render_cache = False
                render.use_overwrite = True
                render.use_placeholder = False
                image_settings.file_format = "PNG"
                image_settings.color_mode = "RGBA"
                image_settings.color_depth = "8"
                image_settings.compression = 0  # Default:15
                image_settings.color_management = "FOLLOW_SCENE"

                # Meta Data
                render.metadata_input = "SCENE"
                render.use_stamp_date = True
                render.use_stamp_time = True
                render.use_stamp_render_time = True
                render.use_stamp_frame = True
                render.use_stamp_frame_range = False
                render.use_stamp_memory = False
                render.use_stamp_hostname = False
                render.use_stamp_camera = True
                render.use_stamp_lens = False
                render.use_stamp_scene = True
                render.use_stamp_marker = False
                render.use_stamp_filename = True
                render.use_stamp_sequencer_strip = False
                render.use_stamp_note = False
                render.use_stamp = False

                # Post Processing
                render.use_compositing = True
                render.use_sequencer = True
                render.dither_intensity = 1

            case _:
                raise Exception("Unsupported Render Settings")

        return {"FINISHED"}


class ExploreRenderOutputPath(Operator):
    """RenderOutput경로를 탐색기로 연다.
    """
    bl_idname = "render.explore_render_output_path"
    bl_label = "Explore Render Output Path"

    @classmethod
    def poll(cls, context):
        scene = context.scene
        render = scene.render
        output_path = render.filepath
        return True if output_path and output_path != "" else False

    def execute(self, context):
        output_path: str = context.scene.render.filepath
        dit_path: str = os.path.dirname(output_path)
        explore_path(dit_path)
        return {"FINISHED"}
