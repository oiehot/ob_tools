import bpy
from bpy.types import (
    Object, Material,
    Brush,
    GreasePencil,
    GPencilLayer,
    MaterialGPencilStyle,
)


BLACK = (0.0, 0.0, 0.0, 1.0)
WHITE = (1.0, 1.0, 1.0, 1.0)


def is_grease_pencil_object(obj: Object) -> bool:
    return True if obj.type == "GPENCIL" else False


def get_grease_pencil_object(name: str) -> GreasePencil:
    raise NotImplementedError


def has_grease_pencil_layer(gpencil: GreasePencil, name: str) -> bool:
    return True if name in gpencil.layers else False


def get_grease_pencil_layer(gpencil: GreasePencil, name: str) -> GPencilLayer | None:
    if has_grease_pencil_layer(gpencil, name):
        return gpencil.layers[name]
    else:
        return None


def clear_grease_pencil_layer(layer: GPencilLayer):
    """GPencilLayer의 모든 스트로크를 제거한다.
    """
    layer.clear()


def has_grease_pencil_brush(name: str) -> bool:
    return True if name in bpy.data.brushes and bpy.data.brushes[name].use_paint_grease_pencil else False


def get_grease_pencil_brushes() -> list[Brush]:
    brushes = [brush for brush in bpy.data.brushes if brush.use_paint_grease_pencil]
    return brushes


def get_grease_pencil_brush(name: str) -> Brush | None:
    if has_grease_pencil_brush(name):
        return bpy.data.brushes[name]
    else:
        return False


def set_current_grease_pencil_brush(name: str):
    brush = get_grease_pencil_brush(name)
    if brush:
        bpy.context.tool_settings.gpencil_paint.brush = brush
    else:
        raise Exception(f"GreasePencil용 브러시를 찾을 수 없음 ({name})")


def create_grease_pencil_brush(gpencil: GreasePencil, name: str) -> Brush:
    raise NotImplementedError
    brush = bpy.data.brushes.new(name=name, mode="GPENCIL")
    brush.gpencil_tool = "DRAW"
    brush.color = (0.0, 0.0, 0.0)
    brush.size = 10
    brush.strength = 1.0
    brush.pen_sensitivity_factor = 1.0
    brush.gpencil_settings.icon_id = 0
    gpencil.brushes.link(brush)


def create_grease_pencil_material(name: str) -> Material:
    """GreasePencil용 Material을 생성한다.
    이미 있으면 재사용한다.
    """
    # mat: Material = None

    if name in bpy.data.materials:
        mat = bpy.data.materials[name]
    else:
        mat = bpy.data.materials.new(name)

    # GreasePencil용 재질이 아니면 세팅한다.
    if not mat.is_grease_pencil:
        bpy.data.materials.create_gpencil_data(mat)
        style = get_grease_pencil_style_from_material(mat)
        set_grease_pencil_style(style)

    return mat


def is_grease_pencil_material(material: Material) -> bool:
    return True if material.grease_pencil else False


def get_grease_pencil_style_from_material(material: Material) -> MaterialGPencilStyle:
    return material.grease_pencil


def set_grease_pencil_style(style: MaterialGPencilStyle,
                            stroke:bool=True,
                            stroke_color=BLACK,
                            fill:bool=False,
                            fill_color=WHITE,
                            ):
    # Stroke
    style.show_stroke = True
    style.mode = "LINE"
    style.color = stroke_color
    # Fill
    style.show_fill = fill
    style.fill_style = "SOLID"
    style.fill_color = fill_color


def get_material_index_in_grease_pencil(gpencil: GreasePencil, material_name: str) -> int:
    """GreasePencil에 등록된 재질의 Index를 얻는다.
    재질이 등록되어 있지 않으면 -1을 리턴한다.
    """
    return gpencil.materials.find(material_name)


def set_grease_pencil_active_material_by_idx(gpencil_object: GreasePencil, index: int):
    # gpencil.materials.active_index = index
    gpencil_object.active_material_index = index


def set_grease_pencil_active_material_by_name(gpencil_object: Object, material_name: str) -> bool:
    """재질의 이름을 통해 GreasePencil에 등록된 재질을 활성화(선택) 한다.
    """
    assert(gpencil_object.type == "GPENCIL")
    gpencil = gpencil_object.data

    idx: int = get_material_index_in_grease_pencil(gpencil, material_name)
    if idx > 0:
        set_grease_pencil_active_material_by_idx(gpencil_object, idx)
        return True
    else:
        return False


def get_material_in_grease_pencil(gpencil: GreasePencil, material_name: str) -> Material | None:
    """이름으로 GreasePencil에 등록된 재질을 찾는다.
    """
    return gpencil.materials.get(material_name)


def has_material_in_grease_pencil(gpencil: GreasePencil, material_name: str) -> bool:
    """GreasePencil에 특정 이름을 가진 Material이 있는가?
    """
    # return True if get_material_index_in_grease_pencil(gpencil, material_name) > 0 else False
    return True if material_name in gpencil.materials else False


def add_material_to_grease_pencil(gpencil: GreasePencil, material: Material):
    """GreasePencil용 재질을 GreasePencil에 등록합니다.
    GreasePencil에 등록된 재질만 DrawMode시 사용할 수 있습니다.
    """
    if not is_grease_pencil_material(material):
        raise Exception(f"GreasePencil에는 GreasePencil용 Material만 추가할 수 있습니다 (name:{material.name})")
    if material.name not in gpencil.materials:
        gpencil.materials.append(material)


def cleat_materials_in_grease_pencil(gpencil: GreasePencil):
    """GreasePencil에 등록된 재질들을 모두 제거한다.
    """
    gpencil.materials.clear()


def remove_all_grease_pencil_materials():
    """씬의 모든 GreasePencil용 Material을 제거한다.
    """
    materials = [mat for mat in bpy.data.materials if mat.grease_pencil]
    for material in materials:
        bpy.data.materials.remove(material)


# def print_gpencil_material(material: Material):
#     style:MaterialGPencilStyle = material.grease_pencil
#     pass


def print_grease_pencil_layer(layer: GPencilLayer):
    print(f"type: {type(layer)}")
    print(f"info(Name): {layer.info}")
    print(f"use_mask_layer: {layer.use_mask_layer}")
    print(f"use.onion_skinng: {layer.use_onion_skinning}")
    print(f"hide: {layer.hide}")
    print(f"lock: {layer.lock}")
    print(f"blend_mode: {layer.blend_mode}")
    print(f"opacity: {layer.opacity}")


def print_grease_pencil(gpencil: GreasePencil):
    print(f"Layers:")
    for layer in gpencil.layers:
        print_grease_pencil_layer(layer)
    return True