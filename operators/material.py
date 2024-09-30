import bpy
from bpy.props import EnumProperty
from bpy.types import Operator, Material

from ..functions.context import (
    is_object_mode,
    has_selected_objects
)
from ..functions.material import (
    get_material, get_random_rgba_tuple,
    has_materials_data, has_material,
)
from ..functions.viewport import update_viewport

COPIED_MATERIALS_KEY: str = "_copied_materials"


class CopyMaterial(Operator):
    """현재 선택된 오브젝트 또는 Faces의 재질을 기억해둔다.
    """
    bl_idname = "material.copy_material"
    bl_label = "Copy Material"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        materials: list[Material] = []

        if len(context.selected_objects) == 0:
            return {"CANCELLED"}

        obj = context.selected_objects[0]

        if not has_materials_data(obj):
            return {"CANCELLED"}

        for material in obj.data.materials:
            materials.append(material)

        if len(materials) > 0:
            bpy.context.scene[COPIED_MATERIALS_KEY] = materials
            print(f"Copy Material: {list(map(lambda m: m.name, materials))}")

        return {'FINISHED'}


class PasteMaterial(Operator):
    bl_idname = "material.paste_material"
    bl_label = "Paste Material"

    @classmethod
    def poll(cls, context):
        # TODO: 오브젝트가 선택되어 있고 복사된 값이 있을 때 True
        return True

    def execute(self, context):
        # 기억해둔 재질 중 첫번째 것만 현재 선택된 오브젝트 또는 Faces에 지정한다.
        materials: list[Material] = []

        if COPIED_MATERIALS_KEY in bpy.context.scene:
            materials = bpy.context.scene[COPIED_MATERIALS_KEY]
        if len(materials) <= 0:
            return {"CANCELLED"}

        # 현재 선택된 오브젝트에 복사해두엇던 재질을 지정한다.
        selected_objects = bpy.context.selected_objects
        first_material: Material = materials[0]
        for obj in selected_objects:
            if not has_materials_data(obj):
                print(f"Paste Material: {obj.name} has no materials property => SKIP")
                continue
            print(f"Paste Material: {first_material.name} => {obj.name}")
            obj.data.materials.clear()
            obj.data.materials.append(first_material)

        # 재질 수정 후 변화를 즉시 반영하기 위해 뷰포트를 업데이트 한다.
        update_viewport()

        return {'FINISHED'}


class CreateAndAssignMaterial(Operator):
    """현재 선택된 Object또는 Faces에 특정 재질을 입힌다.
    재질이 없으면 새로 생성한다.
    """
    bl_idname = "material.create_and_assign_material"
    bl_label = "Toggle Viewport Face Orientation"

    COLORSET: dict = {
        "RED": (1, 0, 0, 1),
        "BLUE": (0, 0, 1, 1),
        "GREEN": (0, 1, 0, 1),
        "WHITE": (1, 1, 1, 1),
        "GRAY": (0.3, 0.3, 0.3, 1),
        "BLACK": (0, 0, 0, 1),
    }

    color: EnumProperty(
        name="Color",
        items=(
            ("RANDOM", "Random", "Random Color"),
            ("RED", "Red", "Red Color"),
            ("GREEN", "Green", "Green Color"),
            ("BLUE", "Blue", "Blue Color"),
            ("WHITE", "White", "White Color"),
            ("GRAY", "Gray", "Gray Color"),
            ("BLACK", "Black", "Black Color"),
            ("CHECKER", "Checker", "Checker Color"),
        )
    )

    def _setup_checker_material(self, material: Material) -> None:
        """지정한 재질을 CheckTexture로 연결된 재질로 수정한다.
        """
        X, Y = 300, 300
        material.use_nodes = True
        nodes = material.node_tree.nodes

        # 기존 노드 제거
        for node in nodes:
            nodes.remove(node)

        print(f"TODO: UVMap노드 생싱 후 연결 필요.")

        # Principled BSDF 노드 생성
        bsdf_node = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf_node.location = (X + 300, Y)

        # Check Texture 노드 생성 및 설정
        checker_node = nodes.new("ShaderNodeTexChecker")
        checker_node.location = (X, Y)
        checker_node.inputs["Color1"].default_value = (0.7, 0.7, 0.7, 1.0)
        checker_node.inputs["Color2"].default_value = (0.35, 0.35, 0.35, 1.0)
        checker_node.inputs["Scale"].default_value = 10.0  # Scale 값을 2.0으로 설정

        # Output 노드 찾기
        output_node = nodes.new("ShaderNodeOutputMaterial")
        output_node.location = (X + 600, Y)

        # 노드들을 연결한다.
        links = material.node_tree.links
        links.new(checker_node.outputs["Color"], bsdf_node.inputs["Base Color"])
        links.new(bsdf_node.outputs["BSDF"], output_node.inputs["Surface"])

    def _create_material(self, material_name: str, color_id: str) -> Material:
        """특정 타입의 컬러에 맞는 재질을 생성한다.
        """
        material: Material = bpy.data.materials.new(name=material_name)
        if color_id in self.COLORSET:
            material.diffuse_color = self.COLORSET[color_id]
        elif color_id == "RANDOM":
            material.diffuse_color = get_random_rgba_tuple()
        elif color_id == "CHECKER":
            self._setup_checker_material(material)
        else:
            raise Exception(f"Unsupported Color ID: {color_id}")
        return material

    @classmethod
    def poll(cls, context):
        return is_object_mode() and has_selected_objects()

    def execute(self, context):
        color_id: str = str(self.color)
        color_name: str = color_id.capitalize()

        # 재질 준비
        material: Material | None = None
        material_name: str = f"M_{color_name}"

        if color_id == "RANDOM":
            material_name = f"{material_name}.001"

        if has_material(material_name) and color_id != "RANDOM":
            material = get_material(material_name)
        else:
            material = self._create_material(material_name, color_id)

        # 선택된 오브젝트들에 준비된 재질을 지정한다.
        for obj in bpy.context.selected_objects:
            if obj.type in ["MESH", "FONT"]:
                obj.data.materials.clear()
                obj.data.materials.append(material)

        return {'FINISHED'}


class SelectObjectsWithSameMaterial(Operator):
    """현재 선택된 Object에서 사용 중인 Material을 사용하는 모든 오브젝트들을 선택한다.
    선택된 Object에 연결된 Material이 없다면 경고를 출력한다.
    선택된 Object에 두 개 이상의 Material이 있는 경우 해당 Material들을 사용중인 모든 오브젝트가 선택은 일단 되나 경고를 출력한다.
    선택된 Object가 여러 개라면 선택된 오브젝트들에서 사용 중인 모든 Material을 대상으로 한다.
    """
    bl_idname = "material.select_objects_with_same_material"
    bl_label = "Select Objects with Same Material"

    @classmethod
    def poll(cls, context):
        """재질을 가지고 있는 오브젝트가 1개 이상 선택되어 있어야만 한다.
        """
        return len(context.selected_objects) > 0

    def execute(self, context):
        """현재 선택중인 오브젝트들에서 사용중인 Material을 사용하는 모든 오브젝트들을 선택한다.
        """
        selected_objects = context.selected_objects
        materials = set()

        # 선택된 오브젝트에서 사용 중인 재질을 수집
        for obj in selected_objects:
            if obj.type == "MESH" and obj.data.materials:
                materials.update(obj.data.materials)

        # 선택된 오브젝트들에 재질이 없는 경우 경고 출력
        if not materials:
            self.report({"WARNING"}, "선택된 오브젝트에 재질이 할당되지 않았습니다.")
            return {"CANCELLED"}

        # 선택된 오브젝트에 두 개 이상의 재질이 있는 경우 경고 출력
        if len(materials) > 1:
            self.report({"WARNING"}, "선택된 오브젝트에 두 개 이상의 재질이 할당되어 있습니다.")

        # 모든 오브젝트에서 동일한 재질을 사용하는 오브젝트 선택
        for obj in bpy.data.objects:
            if obj.type == "MESH" and obj.data.materials:
                for mat in obj.data.materials:
                    if mat in materials:
                        obj.select_set(True)
                        break

        return {"FINISHED"}

class ClearUnusedMaterials(Operator):
    bl_idname = "material.clear_unused_materials"
    bl_label = "Clear Unused Materials"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        for material in bpy.data.materials:
            if not material.users and not material.use_fake_user:
                print(f"RemoveMaterial: {material.name}")
                bpy.data.materials.remove(material)

        # 재질 수정 후 변화를 즉시 반영하기 위해 뷰포트를 업데이트 한다.
        update_viewport()

        self.report({"INFO"}, f"Removed unused materials.")

        return {'FINISHED'}