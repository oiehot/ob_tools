import bpy
from bpy.types import Object


def delete_object(obj: Object):
    bpy.data.objects.remove(obj, do_unlink=True)
