import bpy

from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper
    )

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
    Operator,
    PropertyGroup,
    Panel
)

from .format import Field

class ImportField(Operator, ImportHelper):
    """Import an FE14 Field"""
    bl_idname = "import_scene.fe14_field"
    bl_label = "Import FE14 Field"
    filename_ext = ".bin"
    
    filter_glob: StringProperty(
        default="*.bin",
        options={'HIDDEN'},
        )

    filepath: StringProperty(
        subtype='FILE_PATH', 
        options={'SKIP_SAVE'}
        )
    
    def execute(self, context):
        return {'FINISHED'}

classes = [
    ImportField
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == '__main__':
    register()