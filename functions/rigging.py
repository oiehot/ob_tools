import json
import os

import bpy
from bpy.types import (
    Object, Mesh,
    Armature, ArmatureModifier,
    Bone, BoneCollection,
    ShapeKey
)

from ..encoders.rigging import ObjectVertexGroupEncoder
from ..utils.file import makedir


def get_armature_modifier(obj: Object) -> ArmatureModifier | None:
    for modifier in obj.modifiers:
        if type(modifier) == ArmatureModifier and modifier.type == "ARMATURE":
            return modifier
    return None


def has_armature_modifier(obj: Object) -> bool:
    for modifier in obj.modifiers:
        if modifier.type == "ARMATURE":
            return True
    return False


def create_armature_modifier(obj: Object, modifier_name: str, armature: Armature = None) -> ArmatureModifier:
    modifier: ArmatureModifier = obj.modifiers.new(name=modifier_name, type="ARMATURE")
    modifier.object = armature
    return modifier


def remove_armature_modifiers(obj: Object) -> int:
    count: int = 0
    for modifier in obj.modifiers:
        if modifier.type == "ARMATURE":
            obj.modifiers.remove(modifier)
            count += 1
    return count


def has_vertex_groups(obj: Object) -> bool:
    return True if len(obj.vertex_groups) > 0 else False


def get_parent(obj: Object) -> Object | None:
    return obj.parent


def get_armature_parent(obj: Object) -> Armature | None:
    if obj.parent and obj.parent.type == "ARMATURE":
        return obj.parent
    else:
        return False


def has_armature_parent(obj: Object) -> bool:
    if obj.parent and obj.parent.type == "ARMATURE":
        return True
    return False


def is_rigged_object(obj: Object) -> bool:
    """리깅된 오브젝트인지 여부를 리턴한다.

    리깅된 오브젝트 여부의 조건은 Armature 모디파이어를 가지고 있고
    그 Armature모디파이어 설정된 Armature오브젝트로
    해당 Object가 Parent되어 있는 경우를 말한다.
    """
    armature_modifier = get_armature_modifier(obj)
    armature_parent = get_parent(obj)
    if obj.type == "MESH" and armature_parent and armature_modifier:
        if armature_parent == armature_modifier.object:
            return True
    return False


def is_rig_attached(obj: Object) -> bool:
    armature_modifier = get_armature_modifier(obj)
    armature_parent = get_armature_parent(obj)
    if not armature_modifier or not armature_parent:
        return False
    if armature_modifier.object == armature_parent:
        return True


def remove_vertex_groups(obj: Object) -> bool:
    if len(obj.vertex_groups) > 0:
        obj.vertex_groups.clear()
        return True
    return False


def detach_rigmesh(obj: Object, armature_modifier_remove: bool = True, vertex_group_remove: bool = False,
                   unparent: bool = True) -> None:
    """Armature에서 MeshObject를 떼어낸다.
    """
    if not obj and obj.type != "MESH":
        raise Exception("Mesh 오브젝트만 사용 가능함.")
    if armature_modifier_remove:
        remove_armature_modifiers(obj)
    if vertex_group_remove:
        remove_vertex_groups(obj)
    if unparent:
        if obj.parent:
            if obj.parent.type == "ARMATURE":
                obj.parent = None


def attach_rigmesh(obj: Object, modifier_name: str, armature: Armature) -> None:
    """MeshObject를 Armature에 붙인다.
    """
    if not obj and obj.type != "MESH":
        raise Exception("Mesh 오브젝트만 사용 가능함.")
    remove_armature_modifiers(obj)
    create_armature_modifier(obj, modifier_name, armature)
    obj.parent = armature


def print_vertex_groups(obj: Object):
    if obj.type != "MESH":
        return
    print(f"{obj.name} (MeshObject)")
    for vertex_group in obj.vertex_groups:
        print(f"\t{vertex_group.name} (VertexGroup)")
        for vertex in obj.data.vertices:
            try:
                weight = vertex_group.weight(vertex.index)
                print(f"\t\tVertex {vertex.index} (weight: {weight})")
            except RuntimeError:
                continue


def clear_vertex_groups(obj: Object):
    obj.vertex_groups.clear()


def save_object_vertex_groups(obj: Object, path: str = None) -> bool:
    """주어진 MeshObject의 VertexGroup들을 json 파일로 저장한다.
    """
    if obj is None:
        return False
    try:
        makedir(path)  # 디렉토리가 없으면 파일이 생성되지 않으므로 미리 준비해둔다.
        with open(path, "w", encoding="utf-8") as file:
            json.dump(obj, file, cls=ObjectVertexGroupEncoder, ensure_ascii=False, sort_keys=False, indent=4)
    except:
        return False
    return True


def load_object_vertex_groups(path: str, obj: Object) -> bool:
    """VertexGroup들을 저장한 json파일로 주어진 MeshObject의 VertexGroup들을 생성한다. (로드한다)
    """
    if not os.path.exists(path):
        return False

    with open(path, "r") as file:
        root = json.load(file)

        # 모든 VertexGroup들을 제거한다.
        obj.vertex_groups.clear()

        for vg_data in root["vertex_groups"]:
            # 새 VertexGroup을 만든다.
            vg = obj.vertex_groups.new(name=vg_data["name"])

            for vtx_data in vg_data["data"]:
                if vtx_data["weight"] > 0:
                    vg.add([vtx_data["index"]], vtx_data["weight"], "REPLACE")
    return True


def create_bone_collection(armature: Armature, name: str) -> BoneCollection:
    armature.collections.new(name=name)


def get_bone_collection(armature: Armature, name: str) -> BoneCollection:
    return armature.collections[name]


def get_bone_collections(armature: Armature) -> list[BoneCollection]:
    return list(armature.collections)


def has_bone_collection(armature: Armature, name: str) -> bool:
    return name in armature.collections


def set_bone_collections_visible(armature: Armature, collection_names: list[str], visible: bool):
    collections = armature.collections
    for name in collection_names:
        if name in collections:
            collections[name].is_visible = visible


def set_all_bone_collections_visible(armature: Armature, visible: bool):
    collections = armature.collections
    for collection in collections:
        collection.is_visible = visible


def remove_bone_collection(armature: Armature, name: str):
    collection = armature.collections[name]
    armature.collections.remove(collection)


def remove_blank_collections(armature) -> int:
    count: int = 0
    for collection in armature.collections:
        if len(collection.bones) <= 0:
            armature.collections.remove(collection)
            count += 1
    return count


def get_collection_bones(collection: BoneCollection) -> list[Bone]:
    return list(collection.bones)


def bone_collection_clear(collection) -> int:
    count: int = 0
    bones = list(collection.bones)
    for bone in bones:
        collection.unassign(bone)
        count += 1
    return count


def get_shape_keys(mesh: Mesh) -> list[ShapeKey]:
    return list(mesh.shape_keys.key_blocks)


def get_shape_key(mesh: Mesh, name: str) -> ShapeKey | None:
    for shape_key in get_shape_keys(mesh):
        if shape_key.name == name:
            return shape_key
    return None


def get_shape_key_value(mesh: Mesh, name: str) -> float:
    shape_key = get_shape_key(mesh, name)
    if shape_key:
        return shape_key.value
    else:
        raise Exception(f"Invalid ShapeKey Name ({name})")


def get_selected_armatures() -> list[Armature]:
    """선택된 오브젝트와 연관된 Armature들을 리턴한다.
    """
    selected_armature = [obj.data for obj in bpy.context.selected_objects if obj.type == "ARMATURE"]
    selected_meshes_armature = [get_armature_modifier(obj).object.data for obj in bpy.context.selected_objects if
                                obj.type == "MESH"
                                if has_armature_modifier(obj)]
    return list(set(selected_armature) | set(selected_meshes_armature))
