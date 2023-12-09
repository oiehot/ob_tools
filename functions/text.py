import bpy
from bpy.types import Text


def has_text(name: str) -> bool:
    return True if bpy.data.texts.get(name) else False


def new_text(name: str, use_fake_user: bool = True) -> Text:
    text: Text = bpy.data.texts.new(name)
    text.use_fake_user = use_fake_user
    return text


def remove_text(name: str) -> bool:
    text = bpy.data.texts.get(name)
    if text:
        bpy.data.texts.remove(text)
        return True
    return False


def remove_all_texts() -> int:
    count: int = 0
    for name, text in bpy.data.texts.items():
        bpy.data.texts.remove(text)
        count += 1
    return count


def get_text(name: str) -> Text | None:
    return bpy.data.texts.get(name)


def get_selection_end(text: Text) -> tuple:
    row: int = text.select_end_line_index
    column: int = text.select_end_character
    return (row, column)


def get_selection_begin(text: Text) -> tuple:
    row: int = text.current_line_index
    column: int = text.current_character
    return (row, column)


def get_cursor_position(text: Text) -> tuple:
    row: int = text.select_end_line_index
    column: int = text.select_end_character
    return (row, column)


def move_cursor(text: Text, row: int, column: int):
    text.current_line_index = row
    text.current_character = column
    text.select_end_line_index = text.current_line_index
    text.select_end_character = text.current_character


def move_cursor_to_start(text: Text):
    move_cursor(text, 0, 0)


def move_cursor_to_end(text: Text):
    move_cursor(text, row=len(text.lines) - 1, column=len(text.current_line.body))


def write_line_to_end(text: Text, line: str) -> None:
    move_cursor_to_end(text)
    text.write(line)
