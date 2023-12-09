addon_keymaps = []


def register():
    # wm = bpy.context.window_manager
    # if wm.keyconfigs.addon:
    #     km = wm.keyconfigs.addon.keymaps.new(name='3D View Generic', space_type='VIEW_3D')
    #     kmi = km.keymap_items.new('wm.call_menu_pie', 'Z', 'PRESS', alt=False)
    #     kmi.properties.name = MainPieMenu.bl_idname
    #     addon_keymaps.append((km, kmi))
    pass


def unregister():
    # wm = bpy.context.window_manager
    # kc = wm.keyconfigs.addon
    # if kc:
    #     for km, kmi in addon_keymaps:
    #         km.keymap_items.remove(kmi)
    # addon_keymaps.clear()
    pass
