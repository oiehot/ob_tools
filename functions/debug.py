import bpy

DEFAULT_INDENT_SPACE: int = 4


def _get_indent_str(indent: int) -> str:
    return " " * indent


def print_mesh(mesh, indent: int = 0) -> None:
    indent_str: str = _get_indent_str(indent)
    print(indent_str + f"{mesh.name} (Mesh)")


def print_material(material, indent: int = 0) -> None:
    indent_str: str = _get_indent_str(indent)
    print(indent_str + f"{material.name} (Material)")


def print_object(obj, indent: int = 0) -> None:
    indent_str: str = _get_indent_str(indent)
    print(indent_str + f"{obj.name} (Object)")

    if obj.type in ["MESH"]:
        mesh = obj.data
        print_mesh(mesh, indent + DEFAULT_INDENT_SPACE)
        for material in obj.data.materials:
            print_material(material, indent + DEFAULT_INDENT_SPACE)


def print_collection(collection, indent: int = 0) -> None:
    indent_str: str = _get_indent_str(indent)
    print(indent_str + f"{collection.name} (Collection)")
    for col in collection.children:
        print_collection(col, indent + DEFAULT_INDENT_SPACE)
    for obj in collection.objects:
        print_object(obj, indent + DEFAULT_INDENT_SPACE)


def print_scene(scene, indent: int = 0) -> None:
    indent_str: str = _get_indent_str(indent)
    print(indent_str + f"{scene.name} (Scene)")
    print_collection(scene.collection, indent + DEFAULT_INDENT_SPACE)


def print_all(indent: int = 0) -> None:
    indent_str: str = _get_indent_str(indent)
    print(indent_str + f"Root")
    for scene in bpy.data.scenes:
        print_scene(scene, indent + DEFAULT_INDENT_SPACE)
