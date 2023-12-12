from bpy.types import UILayout


def create_gridflow_at_layout(layout: UILayout, columns: int = 3, header_text: str = None):
    assert (type(layout) == UILayout)
    column = layout.column()
    box = column.box()
    box.scale_y = 0.85
    if header_text and header_text != "":
        header_row = box.row()
        header_row.scale_y = 0.5
        header_row.alignment = "CENTER"
        header_row.label(text=header_text)
    grid_flow = box.grid_flow(
        row_major=True,
        columns=columns,
        even_columns=False,
        even_rows=False,
        align=True)
    return grid_flow
