import bpy
from bpy.props import StringProperty
from bpy.types import Operator


class MessageBox(Operator):
    """팝업창에 메시지를 출력한다.

    bpy.ops.ui.msgbox(message="Hello")
    bpy.ops.ui.msgbox("INVOKE_DEFAULT", message="Hello")
    """
    bl_idname = "ui.msgbox"
    bl_label = "Message Box"

    text: StringProperty(
        name="Text",
        description="Show text to simple box",
        default=""
    )

    def execute(self, context):
        self.report({"INFO"}, f"{self.text}")
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.label(text=self.text)


# TODO: DisplayLongText 오퍼레이터 작업 필요
class DisplayLongText(bpy.types.Operator):
    bl_idname = "text.display_long_text"
    bl_label = "Display Long Text"

    def execute(self, context):
        # 긴 텍스트 생성
        long_text = "여기에 매우 긴 텍스트를 넣습니다.\n" * 1000

        # 텍스트 블록 생성
        text_block = bpy.data.texts.new("LongText")
        text_block.from_string(long_text)

        # 텍스트 에디터로 전환하고 생성된 텍스트 블록 선택
        for area in bpy.context.screen.areas:
            if area.type == 'TEXT_EDITOR':
                area.spaces.active.text = text_block
                break

        return {'FINISHED'}
