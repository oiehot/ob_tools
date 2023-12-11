import bpy
from bpy.types import (
    Operator,
    Object, Material,
    Brush,
    GreasePencil,
    GPencilLayer,
    MaterialGPencilStyle,
)
from bpy.props import BoolProperty, EnumProperty, StringProperty, FloatVectorProperty
from ..functions.context import get_active_object_by_type
from ..functions.gpencil import (
    has_grease_pencil_brush,
    set_current_grease_pencil_brush,
    print_grease_pencil,
    create_grease_pencil_material,
    add_material_to_grease_pencil,
    get_material_index_in_grease_pencil,
    set_grease_pencil_active_material_by_name,
    get_grease_pencil_style_from_material,
)


class SetBrushAndMaterial(Operator):
    bl_idname = "gpencil.set_brush_and_color"
    bl_label = "Set Brush and Color"
    set_brush: BoolProperty(name="Set Brush", description="Set Brush", default=False)
    set_material: BoolProperty(name="Set Material", description="Set Material", default=False)
    brush_name: StringProperty(name="Brush Name", description="Brush Name", default="Ink Pen", maxlen=80)
    material_name: StringProperty(name="Material Name", description="Material Name", default="GPM_Material", maxlen=80)
    show_stroke: BoolProperty(
        name="Show Stroke",
        description="Show stroke",
        default=True
    )
    stroke_color: FloatVectorProperty(
        name="Stroke Color",
        subtype="COLOR",
        size=4, min=0.0, max=1.0,
        default=(1.0, 1.0, 1.0, 1.0)
    )
    show_fill: BoolProperty(
        name="Show Fill",
        description="Show fill",
        default=True
    )
    fill_color: FloatVectorProperty(
        name="Fill Color",
        subtype="COLOR",
        size=4, min=0.0, max=1.0,
        default=(1.0, 1.0, 1.0, 1.0)
    )

    @classmethod
    def poll(cls, context):
        return True if bpy.context.mode == "PAINT_GPENCIL" and get_active_object_by_type("GPENCIL") else False

    def execute(self, context):
        # 현재 선택중인 GreasePencil 얻기.
        gpencil_object: Object = get_active_object_by_type("GPENCIL")
        gpencil: GreasePencil = gpencil_object.data

        if self.set_brush:
            # 브러시 선택
            if not has_grease_pencil_brush(self.brush_name):
                self.report({"ERROR"}, f"Not found brush ({self.brush_name})")
                return {"CANCELLED"}
            set_current_grease_pencil_brush(self.brush_name)

        if self.set_material:
            # 브러시용 재질을 만든다 (없으면 재활용)
            material = create_grease_pencil_material(self.material_name)

            # 스타일 오버라이드
            style = get_grease_pencil_style_from_material(material)
            # Stroke
            style.show_stroke = self.show_stroke
            style.mode = "LINE"
            style.color = self.stroke_color
            # Fill
            style.show_fill = self.show_fill
            style.fill_style = "SOLID"
            style.fill_color = self.fill_color

            # GreasePencil에 해당 재질을 추가한다. 이미 있다면 생략한다.
            add_material_to_grease_pencil(gpencil, material)
            set_grease_pencil_active_material_by_name(gpencil_object, material.name)

        return {'FINISHED'}


class PrintCurrentGreasePencil(Operator):
    bl_idname = "gpencil.print_current_gpencil"
    bl_label = "Print Current GreasePencil"

    @classmethod
    def poll(cls, context):
        objects = [obj for obj in bpy.context.selected_objects if obj.type == "GPENCIL"]
        return True if len(objects) > 0 else False

    def execute(self, context):
        objects = [obj for obj in bpy.context.selected_objects if obj.type == "GPENCIL"]
        for obj in objects:
            print_grease_pencil(obj.data)
        return {'FINISHED'}
