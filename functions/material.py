import random

import bpy
from bpy.types import Object, Material, Image, ShaderNodeTree, ShaderNode


def has_materials_data(obj: Object) -> bool:
    """재질 정보가 있는 데이터를 가진 오브젝트인가?
    """
    data = getattr(obj, "data", None)
    if data:
        materials = getattr(data, "materials", None)
        if materials:
            return True
    return False

def has_material(name: str) -> bool:
    return True if name in bpy.data.materials else False


def get_material(name: str) -> Material | None:
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    else:
        return None


def create_material(name: str, use_nodes: bool = True) -> Material:
    material: Material = bpy.data.materials.new(name=name)
    if material:
        material.use_nodes = use_nodes
    return material


def remove_material(name: str, ignore_users: bool = True) -> None:
    material = bpy.data.materials.get(name)
    if material:
        if not ignore_users and material.users > 0:
            raise Exception(
                f"The material cannot be removed because it is in use (material: {name}, users: {material.users})")
        bpy.data.materials.remove(material)


def assign_material(obj: Object, material: Material, slot_idx: int = 0):
    """특정 오브젝트에 재질을 입힙니다.
    """
    slot_count = len(obj.material_slots)
    if slot_count == 0 and slot_idx == 0:
        obj.data.materials.append(material)
    elif slot_idx >= 0 and slot_idx + 1 <= slot_count:
        obj.material_slots[slot_idx].material = material
    else:
        raise Exception("There is not slot to place the material ({obj.name}, {slot})")


def get_material_name(name: str) -> str:
    return f"M_{name}"


def get_material_slot_count(obj: Object) -> int:
    return len(obj.material_slots)


def add_blank_material_slot(obj: Object):
    prev = len(obj.material_slots)
    obj.data.materials.append(None)
    current = len(obj.material_slots)
    assert (prev + 1 == current)


def get_materials_from_mesh_object(obj: Object) -> list[Material]:
    if obj.type != "MESH":
        raise Exception(f"Is not a MeshObject (name:{obj.name}, type:{obj.type})")
    results = []
    for slot in obj.material_slots:
        if slot.material:
            results.append(slot.material)
    return results


def get_random_rgba_tuple() -> tuple:
    return (
        random.random(),
        random.random(),
        random.random(),
        1.0
    )


def clear_unused_materials() -> None:
    for material in bpy.data.materials:
        if not material.users and not material.use_fake_user:
            bpy.data.materials.remove(material)


def has_image(name: str) -> bool:
    """이미지의 존재 유무.
    """
    return name in bpy.data.images


def get_image(name: str) -> Image:
    """이미지를 얻는다.
    """
    return bpy.data.images.get(name)


def get_image_size(name: str) -> tuple:
    """이미지의 사이즈를 튜플(x, y)로 얻는다.
    """
    img = get_image(name)
    w, h = img.size[0], img.size[1]
    return w, h


def create_image(name: str, width: int, height: int) -> Image:
    """이미지를 생성한다.
    """
    if not has_image(name):
        return bpy.data.images.new(name, width, height)
    else:
        return get_image(name)


def remove_image(name: str) -> None:
    """이미지를 제거한다.
    """
    if has_image(name):
        img = get_image(name)
        bpy.data.images.remove(img)


def get_nodetree(material_name: str) -> ShaderNodeTree:
    """재질의 노드트리를 얻는다.
    """
    material = bpy.data.materials.get(material_name)
    if material and material.use_nodes:
        return material.node_tree
    else:
        raise Exception(f"Cannot obtain the node tree from the material ({material_name})")


def get_node(material_name: str, node_name: str) -> ShaderNode:
    """재질의 노트트리에서 노드를 얻는다.
    """
    node_tree = get_nodetree(material_name)
    return node_tree.nodes.get(node_name)


def get_or_create_shader_node(material_name: str, node_name: str, node_type: str) -> ShaderNode:
    """재질의 노드트리에서 노드를 찾고 없으면 새로 생성한다.
    지정한 타입이 아닌 경우 None을 리턴한다.
    """
    node_tree = get_nodetree(material_name)
    node = node_tree.nodes.get(node_name)
    if node and node.bl_idname == node_type:
        return node
    elif not node:
        node = node_tree.nodes.new(type=node_type)
        node.name = node_name
        return node
    else:
        raise Exception("Cannot obtain the node")


def set_active_shader_node(material_name: str, node_name: str) -> None:
    """특정 노드를 Active 한다.
    """
    node_tree = get_nodetree(material_name)
    node = node_tree.nodes.get(node_name)
    node_tree.nodes.active = node


def export_image(image: Image, filepath: str, file_format: str = "PNG") -> None:
    """이미지 데이터 블럭을 그림 파일로 Export한다.
    """
    if not image.has_data:
        raise Exception("The image has no data")

    if not filepath or filepath == "":
        raise Exception("Invalid filepath")

    image.filepath_raw = filepath
    image.file_format = file_format
    image.save_render(filepath)


def file_format_to_ext(file_format: str) -> str:
    """이미지 파일포맷 Enum을 파일 확장자로 변환해준다.
    예) JPEG => jpg
    """
    formats = {
        "PNG": "png",
        "JPEG": "jpg",
        "TARGA": "tga",
        "TIFF": "tif",
        "WEBP": "webp",
    }
    return formats.get(file_format, file_format.lower())


assert (file_format_to_ext("PNG") == "png")
assert (file_format_to_ext("JPEG") == "jpg")
assert (file_format_to_ext("WEBP") == "webp")
assert (file_format_to_ext("OTHER") == "other")
