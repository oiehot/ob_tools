import os

import bpy
from bpy.props import EnumProperty, IntProperty, FloatProperty, StringProperty
from bpy.types import Object, Operator, Image

from ..functions.context import (
    is_object_mode, get_selected_objects_by_type,
    set_active_object, select_objects, deselect_all,
)
from ..functions.material import export_image
from ..functions.material import file_format_to_ext
from ..functions.material import get_material, create_material, assign_material
from ..functions.material import get_materials_from_mesh_object
from ..functions.material import get_or_create_shader_node, set_active_shader_node
from ..functions.material import has_image, get_image, create_image
from ..utils.text_utils import get_image_size_symbol, float_to_symbol, baketype_to_symbol


def quick_bake(
        bake_type: str,
        high_object: Object,
        low_object: Object,
        width: int = 2048,
        height: int = 2048,
        cage_extrusion: float = 0.15,
        max_ray_distance: float = 0.3,
        margin: int = 16
) -> Image:
    """베이크 한다.
    """
    func_id: str = quick_bake.__name__
    render = bpy.context.scene.render
    bake = bpy.context.scene.render.bake
    cycles = bpy.context.scene.cycles

    # 베이크용 렌더러 설정
    render.use_bake_multires = False
    render.engine = "CYCLES"
    cycles.device = "GPU"
    cycles.bake_type = bake_type

    # 베이크하기 위해 Source, Target(Active) 오브젝트를 선택하고 활성화한다.
    deselect_all()
    select_objects([high_object, low_object])
    set_active_object(low_object)
    print(f"{func_id}: High-poly Object ({high_object.name})")
    print(f"{func_id}: Low-poly Object ({low_object.name})")

    # LowPoly의 MaterialSlot 카운트가 0이면 빈 슬롯을 하나 만든다.
    if len(low_object.material_slots) == 0:
        add_blank_material_slot(low_object)

    # LowPoly의 MaterialSlot 카운트가 1이 아니면 예외처리.
    if len(low_object.material_slots) != 1:
        raise Exception(
            f"The low-poly object to be the target of the bake must have only one material slot ({low_object.name})")

    # 베이크용 재질을 얻는다. 이미 있으면 재활용하고 없으면 새로 만들어 Assign 한다.
    materials: list[Material] = get_materials_from_mesh_object(low_object)
    material: Material = None
    if len(materials) > 0:
        # Assign된 재질이 있는 경우 그것을 사용한다.
        material = materials[0]
        print(f"{func_id}: Reuse Assigned Material ({material.name})")
    else:
        # 동일 이름을 가진 재질을 찾거나 없으면 새로 생성 한 뒤 Assign 한다.
        material_name = f"M_{low_object.name}"
        print(f"{func_id}: Find or Create a Material ({material_name})")
        material = get_material(material_name) or create_material(material_name)  # TODO: PrincipleBSDF 노드로 생성하기
        print(f"{func_id}: Assign Material to Object ({material.name} > {low_object.name})")
        assign_material(low_object, material)

    # 베이크 타겟이 될 이미지 블럭을 만든다. (이미 있다면 제거하고 새로 만든다)
    image_name: str = f"T_{low_object.name}_{baketype_to_symbol(bake_type.capitalize())}_{get_image_size_symbol(width, height)}_R{float_to_symbol(max_ray_distance)}_C{float_to_symbol(cage_extrusion)}"
    print(f"{func_id}: Get or Create a Image ({image_name})")
    image: Image = get_image(image_name) if has_image(image_name) else create_image(image_name, width, height)

    # 재질의 노드 트리에 텍스쳐 노드를 생성한다.
    texture_node_name: str = f"TN_{low_object.name}_{bake_type.capitalize()}"
    print(f"{func_id}: Get or Create a TextureNode ({material.name} > node_tree > {texture_node_name})")
    texture_node = get_or_create_shader_node(material.name, texture_node_name, "ShaderNodeTexImage")

    # 텍스쳐 노드에 이미지를 지정한다.
    print(f"{func_id}: Set TextureNode's Image ({texture_node.name} = {image.name})")
    texture_node.image = image

    # 이미지의 컬러스페이스를 설정한다.
    print(f"{func_id}: Set Image Colorspace ({image.name})")
    image.colorspace_settings.name = "Non-Color"

    # 베이크 타겟이 될 Image가 지정된 TextureNode를 Active 해둔다. 그래야 이 이미지로 Bake된다.
    print(f"{func_id}: Set Active ShaderNode ({material.name} > node_tree > {texture_node.name})")
    set_active_shader_node(material.name, texture_node.name)

    # 베이크 시작.
    print(
        f"{func_id}: Start a Bake (type={bake_type}, width={width}, height={height}, object={low_object.name}, material={material.name}, textue_node={texture_node.name}, image={image.name})")
    # bpy.ops.object.bake(type='COMBINED', pass_filter=set(), filepath="", width=512, height=512, margin=16,
    #                     margin_type='EXTEND', use_selected_to_active=False, max_ray_distance=0, cage_extrusion=0,
    #                     cage_object="", normal_space='TANGENT', normal_r='POS_X', normal_g='POS_Y',
    #                     normal_b='POS_Z', target='IMAGE_TEXTURES', save_mode='INTERNAL', use_clear=False,
    #                     use_cage=False, use_split_materials=False, use_automatic_name=False, uv_layer="")
    bpy.ops.object.bake(type=bake_type,
                        width=width,
                        height=height,
                        margin=margin,
                        use_selected_to_active=True,
                        max_ray_distance=max_ray_distance,
                        cage_extrusion=cage_extrusion,
                        normal_space="TANGENT",
                        normal_r="POS_X",
                        normal_g="POS_Y",
                        normal_b="POS_Z",
                        target="IMAGE_TEXTURES",  # or VERTEX_COLORS
                        use_clear=True,
                        use_cage=False,
                        use_split_materials=False,
                        use_automatic_name=False,
                        save_mode="INTERNAL"
                        )

    return image


def get_selected_high_low() -> tuple | None:
    """선택된 메쉬 오브젝트에서 하이폴, 로우폴 순서로 된 튜플을 리턴한다.
    """
    mesh_objects = get_selected_objects_by_type("MESH")
    if len(mesh_objects) > 2:
        return None
    elif len(mesh_objects) < 2:
        return None

    high, low = None, None

    # 폴리곤 수 가 많은 것이 하이폴이 되고 나머지가 로우폴이 된다.
    if len(mesh_objects[0].data.polygons) > len(mesh_objects[1].data.polygons):
        high = mesh_objects[0]
        low = mesh_objects[1]
    else:
        high = mesh_objects[1]
        low = mesh_objects[0]

    return (high, low)


class QuickBakeNormal(Operator):
    """Highpoly의 메쉬를 Lowpoly에 적용하기 위해 Normal을 굽는다.
    """
    bl_idname = "object.quick_bake_normal"
    bl_label = "Quick Bake Normal"

    width: IntProperty(name="Width", default=1024, min=64, max=8192)
    height: IntProperty(name="Height", default=1024, min=64, max=8192)
    cage_extrusion: FloatProperty(name="Cage Extrusion", default=0.15, min=0.01)
    max_ray_distance: FloatProperty(name="Max Ray Distance Extrusion", default=0.3, min=0.01, max=128)
    margin: IntProperty(name="Margin (px)", default=16, min=1, max=64)
    filepath: StringProperty(
        name="File Path",
        description="Save filepath",
        default="",
    )
    file_format: EnumProperty(
        name="File Format",
        items=[
            ("PNG", "PNG", "PNG image format"),
            ("JPEG", "JPEG", "JPG image format"),
            ("TARGA", "TARGA", "TGA image format"),
            ("TIFF", "TIFF", "TIF image format"),
            ("WEBP", "WEBP", "WEBP image format"),
        ],
        default="PNG"
    )

    @classmethod
    def poll(cls, context):
        return True if is_object_mode() and get_selected_high_low() else False

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        # 파일경로가 빠져 있으면 경고.
        if not self.filepath or self.filepath == "":
            self.report({"WARNING"}, "Filepath is empty")
            return {"CANCELLED"}

        # 선택한 오브젝트 중에서 하이폴과 로우폴 메쉬 오브젝트를 얻는다.
        high, low = get_selected_high_low()

        # 굽는다.
        bake_type = "NORMAL"
        image: Image = quick_bake(
            bake_type=bake_type,
            high_object=high,
            low_object=low,
            width=self.width,
            height=self.height,
            cage_extrusion=self.cage_extrusion,
            max_ray_distance=self.max_ray_distance,
            margin=self.margin
        )

        if not image.has_data:
            self.report({"ERROR"}, f"{self.bl_label}: Image was not generated ({image.name})")
            return {"CANCELLED"}

        # 옵션에 따라 파일을 저장한다.
        filepath: str = self.filepath

        # 파일 경로가 디렉토리인 경우 파일명이 자동으로 지정된다.
        if os.path.isdir(filepath):
            ext = file_format_to_ext(self.file_format)
            # 경로를 정규화하고 POSIX 형태로 마무리.
            filepath = os.path.normpath(os.path.join(filepath, f"{filepath}/{image.name}.{ext}")).replace("\\", "/")
        print(f"{self.bl_label}: Save an image file ({filepath})")
        export_image(image, filepath, self.file_format)

        self.report({"INFO"}, f"{self.bl_label}: Image Generated ({filepath})")
        return {"FINISHED"}
