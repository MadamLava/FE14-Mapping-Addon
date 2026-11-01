import bpy
import os

from bpy.props import (
        IntProperty,
        BoolProperty,
        EnumProperty,
        FloatProperty,
        StringProperty,
        PointerProperty,
        FloatVectorProperty,
        CollectionProperty
        )
        
from bpy.types import (
    PropertyGroup,
    Panel
    )  

def string_empty_check(string):
    is_empty = False
    
    if not string == None and (len(string) == 0 or string.isspace()):
        is_empty = True
    
    return is_empty

class FE14_SceneProps(Panel):
    bl_label = "FE14SceneProperties"
    bl_idname = "FE14_PT_ScenePropertiesPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category= "FE14"
    bl_parent_id = ""
    
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        
        vanilla_romfs_path = bpy.context.preferences.addons["io_scene_fe14"].preferences.vanilla_romfs_path
        modded_romfs_path = bpy.context.preferences.addons["io_scene_fe14"].preferences.modded_romfs_path
        
        if (string_empty_check(vanilla_romfs_path) or not os.path.exists(vanilla_romfs_path)) or (string_empty_check(modded_romfs_path) or not os.path.exists(modded_romfs_path)):
            layout.enabled = False

classes = [
    FE14_SceneProps
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == '__main__':
    register()