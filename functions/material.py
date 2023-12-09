import random

import bpy
from bpy.types import Material


def has_material(name: str) -> bool:
    return True if name in bpy.data.materials else False


def get_material(name: str) -> Material | None:
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    else:
        return None


def create_material(name: str) -> Material:
    material: Material = bpy.data.materials.new(name=name)
    return material


def get_material_name(name: str) -> str:
    return f"M_{name}"


def get_random_rgba_tuple() -> tuple:
    return (
        random.random(),
        random.random(),
        random.random(),
        1.0
    )


def clear_unused_materials():
    for material in bpy.data.materials:
        if not material.users and not material.use_fake_user:
            bpy.data.materials.remove(material)
