import bpy


def update_viewport():
    """뷰포트를 강제로 업데이트한다.
    """
    bpy.context.view_layer.update()
    shading = bpy.context.space_data.shading
    current_shading = shading.type
    shading.type = "WIREFRAME"
    shading.type = current_shading
