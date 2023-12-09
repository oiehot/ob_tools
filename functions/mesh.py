import bmesh
import bpy
from bmesh.types import BMesh, BMVert, BMEdge, BMFace

from .context import is_object_mode


def get_selected_vertices() -> list[BMVert]:
    """선택된 버텍스들을 리턴한다.
    엣지가 1개 선택되어 있으면 버텍스 2개가 리턴된다.
    페이스가 1개 선택되어 있으면 엣지는 2개, 버텍스는 4개가 리턴된다.
    """
    if is_object_mode():
        return []
    bm: BMesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
    return [v for v in bm.verts if v.select]


def get_selected_edges() -> list[BMEdge]:
    if is_object_mode():
        return []
    bm: BMesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
    return [e for e in bm.edges if e.select]


def get_selected_faces() -> list[BMFace]:
    if is_object_mode():
        return []
    bm: BMesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
    return [f for f in bm.faces if f.select]
