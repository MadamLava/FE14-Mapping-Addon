from bpy.types import (
        PropertyGroup,
        Operator,
        Panel
        )

from bpy.props import (
        BoolProperty,
        EnumProperty,
        StringProperty,
        FloatProperty,
        IntProperty,
        PointerProperty,
        FloatVectorProperty
        )

class FE14_ObjectProps(Panel):
    bl_label = "FE14 Object Properties"
    bl_idname = "FE14_PT_ObjectDetailsPanel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    
    @classmethod
    def poll(self, context):
        valid = False
        ob = context.object

        if hasattr(ob, 'fe14_props'):
            valid = True

        return valid
        
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        ob = context.object
        fe14_props = ob.fe14_props
        
        col = layout.column(align=True)
        
        row = col.row()
        row.label(text='Object Type')
        row.prop(fe14_props, "object_type", text='')
        row = col.row()
        
        if fe14_props.object_type == 'PART':
            row.label(text='Name')
            row.prop(fe14_props, "name", text='')
            row = col.row()
            row.label(text='BCH Container Name')
            row.prop(fe14_props, "file_name", text='')
            
            row = col.row()
            row.label(text='Part Subtype')
            row.prop(fe14_props, "part_type", text='')
            
            row = col.row()
            row.label(text='Extents 1')
            row.prop(fe14_props, "part_extents_1", text='')
            row = col.row()
            row.label(text='Extents 2')
            row.prop(fe14_props, "part_extents_2", text='')
            row = col.row()
            row.label(text='Visibility Flags(?)')
            row.prop(fe14_props, "part_flags_1", text='')
            row.prop(fe14_props, "part_flags_2", text='')
            row.prop(fe14_props, "part_flags_3", text='')
            row.prop(fe14_props, "part_flags_4", text='')
            
            row = col.row()
            row.label(text='Map Height References')
            row = col.row()
            row.prop(fe14_props, "part_height_1", text='')
            row.prop(fe14_props, "part_height_2", text='')
            row.prop(fe14_props, "part_height_3", text='')
            row = col.row()
            row.label(text='Collision References')
            row = col.row()
            row.prop(fe14_props, "part_collision_1", text='')
            row.prop(fe14_props, "part_collision_2", text='')
            row.prop(fe14_props, "part_collision_3", text='')
            row = col.row()
            row.prop(fe14_props, "part_collision_4", text='')
            row.prop(fe14_props, "part_collision_5", text='')
            row.prop(fe14_props, "part_collision_6", text='')
            row = col.row()
            row.label(text='Effect References')
            row = col.row()
            row.prop(fe14_props, "part_effect_1", text='')
            row.prop(fe14_props, "part_effect_2", text='')
            row.prop(fe14_props, "part_effect_3", text='')
            row = col.row()
            row.prop(fe14_props, "part_effect_4", text='')
            row.prop(fe14_props, "part_effect_5", text='')
            row.prop(fe14_props, "part_effect_6", text='')
            
        if fe14_props.object_type == 'REFER':
            row.label(text='Name')
            row.prop(fe14_props, "name", text='')
            row = col.row()
            row.label(text='Name in Model File')
            row.prop(fe14_props, "file_name", text='')
            row = col.row()
            row.label(text='Source File Name')
            row.prop(fe14_props, "file_origin_name", text='')
            
        if fe14_props.object_type == 'EFFECT':
            row.label(text='Name')
            row.prop(fe14_props, "name", text='')
            row = col.row()
            row.label(text='Effect Name')
            row.prop(fe14_props, "file_name", text='')
            

class FE14_ObjectPropertiesGroup(PropertyGroup):
    name : StringProperty(
        name="Name",
        description="Name of the object within this file"
    )
    
    file_name : StringProperty(
        name="Filename",
        description="Contextual"
    )
    
    file_origin_name : StringProperty(
        name="Source File Name",
        description="Name of the file this object originates from"
    )
    
    object_type : EnumProperty(
        name="Object Type",
        description="Select object type",
        default = "PART",
        items = [
            ('PART', "Part", "A defined object originating from the map file"),
            ('REFER', "Refer", "An instance of a Part, be it from the map's own Parts or a referenced file"),
            ('EFFECT', "Effect", "An instance of an Effect to be associated with a Part"),
            ('HEIGHT', "Height", "A mesh representing map tile corner heights"),
            ('COLLISION', "Collision", "A mesh representing collision data")
        ]
    )
    
    # Part Stuff
    part_type : EnumProperty(
        default = "MAP OBJECT",
        items = [
            ('GROUND', "Ground", "Primary mesh of the Field"),
            ('MAP OBJECT', "Map Object", "Standard Map Object"),
            ('ANANKOS', "Anankos Body Part", "Map object that makes up part of the final Anankos fight. Don't use.")
        ]
    )
    part_extents_1 : FloatVectorProperty(
        default =(10000.0, 10000.0, 10000.0)
    )
    part_extents_2 : FloatVectorProperty(
        default =(-10000.0, -10000.0, -10000.0)
    )
    part_flags_1 : IntProperty(
        default=0
    )
    part_flags_2 : IntProperty(
        default=0
    )
    part_flags_3 : IntProperty(
        default=0
    )
    part_flags_4 : IntProperty(
        default=0
    )
    part_height_1: StringProperty(
        default=''
    )
    part_height_2: StringProperty(
        default=''
    )
    part_height_3: StringProperty(
        default=''
    )
    part_collision_1: StringProperty(
        default=''
    )
    part_collision_2: StringProperty(
        default=''
    )
    part_collision_3: StringProperty(
        default=''
    )
    part_collision_4: StringProperty(
        default=''
    )
    part_collision_5: StringProperty(
        default=''
    )
    part_collision_6: StringProperty(
        default=''
    )
    part_effect_1: StringProperty(
        default=''
    )
    part_effect_2: StringProperty(
        default=''
    )
    part_effect_3: StringProperty(
        default=''
    )
    part_effect_4: StringProperty(
        default=''
    )
    part_effect_5: StringProperty(
        default=''
    )
    part_effect_6: StringProperty(
        default=''
    )