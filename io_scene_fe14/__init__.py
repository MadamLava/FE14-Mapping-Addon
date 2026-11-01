import bpy
import bmesh
import math
import os

### FE14 Field Import/Export Addon ###
# Structurally inspired by General101's Halo Asset Blender Development Toolset

from bpy.props import (
    IntProperty,
    BoolProperty,
    EnumProperty,
    FloatProperty,
    StringProperty,
    PointerProperty,
    FloatVectorProperty
    )

# Import list
from . import global_ui
from . import file_bin

# List of module imports to Register
modules = [
    global_ui,
    file_bin
]

bl_info = {
    "name": "FE14 Mapping Addon",
    "author": "MadamLava",
    "version": (0, 1, 0),
    "blender": (4, 5, 0),
    "description": "Import/Export FE14 Fields.",
    "category": "Import-Export",
}

class FE14AddonPrefs(bpy.types.AddonPreferences):
    bl_idname = __name__
    
    vanilla_romfs_path: StringProperty(
        name = "Vanilla ROMFS Path",
        description = "Path to the vanilla extracted ROMFS assets",
        subtype = "DIR_PATH"
    )
    
    modded_romfs_path: StringProperty(
        name = "Modded ROMFS Path",
        description = "Path to the targeted modded ROMFS assets",
        subtype = "DIR_PATH"
    )
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.label(text="ROMFS Paths:")
        col = box.column(align=True)
        
        row = col.row()
        row.label(text='Vanilla ROMFS Path')
        row.prop(self, "vanilla_romfs_path", text='')
        row = col.row()
        row.label(text='Modded ROMFS Path')
        row.prop(self, "modded_romfs_path", text='')
    
def register():
    bpy.utils.register_class(FE14AddonPrefs)
    for module in modules:
        module.register()

def unregister():
    bpy.utils.unregister_class(FE14AddonPrefs)
    for module in reversed(modules):
        module.unregister()

if __name__ == "__main__":
    register()