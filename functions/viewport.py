import bpy


def update_viewport():
    """뷰포트를 강제로 업데이트한다.
    """
    bpy.context.view_layer.update()
    shading = bpy.context.space_data.shading
    current_shading = shading.type
    shading.type = "WIREFRAME"
    shading.type = current_shading


def set_editmode_overlay_type(context, mode: str):
    """편집모드 오버레이 타입을 변경한다.
    """
    overlay = context.space_data.overlay
    statvis = context.scene.tool_settings.statvis

    # 기본 설정
    overlay.show_edges = True
    overlay.show_faces = True
    overlay.show_face_center = False

    overlay.show_edge_crease = True
    overlay.show_edge_sharp = True
    overlay.show_edge_bevel_weight = True
    overlay.show_edge_seams = True

    overlay.show_extra_indices = False  # 선택 요소의 Index를 표시 (개발자용)

    overlay.show_retopology = False
    overlay.retopology_offset = 0.2
    overlay.show_weight = False
    overlay.show_statvis = False

    overlay.show_extra_edge_length = False
    overlay.show_extra_face_area = False
    overlay.show_extra_edge_angle = False
    overlay.show_extra_face_angle = False

    overlay.show_vertex_normals = False
    overlay.show_split_normals = False
    overlay.show_face_normals = False
    overlay.normals_length = 0.2
    overlay.use_normals_constant_screen_size = False

    overlay.show_freestyle_edge_marks = True
    overlay.show_freestyle_face_marks = True

    match mode:
        case "MEASURE":
            overlay.show_face_center = True
            overlay.show_extra_edge_length = True
            overlay.show_vertex_normals = True
        case "INTERSECT":
            overlay.show_statvis = True
            statvis.type = "INTERSECT"
        case "DISTORT":
            overlay.show_statvis = True
            statvis.type = "DISTORT"
            statvis.distort_min = 0.0872665
            statvis.distort_max = 0.785398
        case "DEVELOP":
            overlay.show_extra_indices = True
            pass


def get_editmode_overlay_type(context) -> str:
    """현재 편집 모드 오버레이 타입을 얻는다.
    """
    overlay = context.space_data.overlay
    statvis = context.scene.tool_settings.statvis
    if overlay.show_face_center and overlay.show_extra_edge_length and overlay.show_vertex_normals:
        return "MEASURE"
    elif overlay.show_statvis and statvis.type == "INTERSECT":
        return "INTERSECT"
    elif overlay.show_statvis and statvis.type == "DISTORT":
        return "DISTORT"
    elif overlay.show_extra_indices:
        return "DEVELOP"
    return "DEFAULT"
