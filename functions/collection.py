import bpy
from bpy.types import Collection, LayerCollection
from mathutils import Vector


def create_collection(name: str) -> Collection:
    """컬렉션을 생성한다.
    """
    if name not in bpy.data.collections:
        new_collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(new_collection)
        return new_collection
    else:
        return bpy.data.collections[name]


def get_all_collections() -> list[Collection]:
    return bpy.data.collections


def get_all_layer_collections_recursive(layer_collection, collection_list: list = None):
    """레이어 컬렉션을 재귀적으로 모은다.
    """
    if not collection_list:
        collection_list = []
    collection_list.append(layer_collection)
    for child_layer_collection in layer_collection.children:
        get_all_layer_collections_recursive(child_layer_collection, collection_list)
    return collection_list


def get_all_layer_collections():
    """뷰 레이어와 그 하위에 있는 모든 레이어 컬렉션을 리턴한다.
    """
    root_layer_collection = bpy.context.view_layer.layer_collection
    return get_all_layer_collections_recursive(root_layer_collection)


def get_layer_collection(name:str) -> LayerCollection:
    root_layer_collection: LayerCollection = bpy.context.view_layer.layer_collection
    result: LayerCollection = find_layer_collection_recursive(root_layer_collection, name)
    if not result:
        raise Exception(f"Not found LayerCollection ({name})")
    return result


def find_layer_collection_recursive(layer_collection: LayerCollection, name:str) -> LayerCollection | None:
    """재귀적으로 특정 이름을 가진 컬렉션을 찾는다.
    """
    if layer_collection.name == name:
        return layer_collection
    for child in layer_collection.children:
        result = find_layer_collection_recursive(child, name)
        if result:
            return result
    return None


def set_active_layer_collection(name: str):
    """특정 이름을 가진 레이어 컬렉션을 활성화한다.
    """
    layer_collection = get_layer_collection(name)
    bpy.context.view_layer.active_layer_collection = layer_collection


def get_collection_bound_box(name:str) -> tuple[Vector, Vector]:
    collection = bpy.data.collections.get(name)
    if not collection:
        raise Exception(f"Not found Collection {name}")

    min_coord = Vector((float("inf"), float("inf"), float("inf")))
    max_coord = Vector((-float("inf"), -float("inf"), -float("inf")))

    for obj in collection.objects:
        if obj.type == "MESH":
            world_vertices = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
            for vert in world_vertices:
                min_coord = Vector((min(min_coord.x, vert.x), min(min_coord.y, vert.y), min(min_coord.z, vert.z)))
                max_coord = Vector((max(max_coord.x, vert.x), max(max_coord.y, vert.y), max(max_coord.z, vert.z)))
    return (min_coord, max_coord)
