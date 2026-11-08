import bpy
import os
import struct
import bmesh
import mathutils
import math

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
from .format import import_field

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
        import_field(self.filepath)
        return {'FINISHED'}

# Stores data about an unresolved pointer reference.
class Pointer():
    def __init__(self, pos, target):
        self.pos = pos
        self.target = target

# A position where a named piece of data lives. Registered in first pass so that pointers can be connected.
# In the second pass, pointers will be iterated, and matched to each Target
class PointerTarget():
    def __init__(self, pos, name):
        self.pos = pos
        self.name = name

class ExportField(Operator, ExportHelper):
    """Export an FE14 Field"""
    bl_idname = "export_scene.fe14_field"
    bl_label = "Export FE14 Field"
    filename_ext = ".bin"
    
    filter_glob: StringProperty(
        default="*.bin",
        options={'HIDDEN'},
        )

    filepath: StringProperty(
        subtype='FILE_PATH', 
        options={'SKIP_SAVE'}
        )
    
    selected_only : BoolProperty(
        name='Export Selected Objects Only',
        description="Only export objects that are selected",
        default=True
    )
    hidden_geo : BoolProperty(
        name='Export Hidden Objects',
        description="Export objects hidden from the viewport",
        default=False
    )
    nonrender_geo : BoolProperty(
        name='Export Non-Render Objects',
        description="Export objects hidden from the render output",
        default=False
    )
    
    def execute(self, context):
        
        print("Exporting...")
        
        filename = os.path.basename(self.filepath)
        
        if self.selected_only:
            objects = bpy.context.selected_objects
        else:
            objects = bpy.context.scene.objects
        
        parts = []
        refers = []
        effects = []
        heights = []
        collisions = []
        
        strings = []
        pointers = []
        targets = []
        files =  []
        
        files.append(filename.split('.')[0])
        strings.append(filename.split('.')[0])
        
        # Obtain unique strings
        for obj in objects:
            if hasattr(obj, 'fe14_props'):
                do_strings = True
                if obj.fe14_props.object_type == 'PART':
                    parts.append(obj)
                if obj.fe14_props.object_type == 'REFER':
                    refers.append(obj)
                if obj.fe14_props.object_type == 'EFFECT':
                    effects.append(obj)
                if obj.fe14_props.object_type == 'HEIGHT':
                    heights.append(obj)
                    do_strings = False
                if obj.fe14_props.object_type == 'COLLISION':
                    collisions.append(obj)
                    do_strings = False
                
                if do_strings:
                    if obj.fe14_props.name not in strings and obj.fe14_props.name != "":
                        strings.append(obj.fe14_props.name)
                        
                    if obj.fe14_props.file_name not in strings and obj.fe14_props.file_name != "":
                        strings.append(obj.fe14_props.file_name)
                        
                    if obj.fe14_props.file_origin_name not in files and obj.fe14_props.file_origin_name != "":
                        files.append(obj.fe14_props.file_origin_name)
                        
                    if obj.fe14_props.file_origin_name not in strings and obj.fe14_props.file_origin_name != "":
                        strings.append(obj.fe14_props.file_origin_name)
                
        with open(self.filepath, 'wb') as file:
            
            # STEP 1: MAP HEADER
            write_int(0, file)
            write_int(0, file)
            write_int(0, file)
            write_int(4, file)
            
            write_int(0, file)
            write_int(0, file)
            write_int(0, file)
            write_int(0, file)
            
            #I dont think the basegame uses this one
            #pointers.append(Pointer(99, "PointerListPointer"))
            
            # stupid magic number that i hate
            write_int(538183203, file)
            
            pointers.append(Pointer(file.tell(), strings[0]))
            write_int(0, file)
            
            # STEP 2: PARTS
            targets.append(PointerTarget(file.tell(), "PartCountPointer"))
            write_int(len(parts), file)
            
            pointers.insert(0, Pointer(file.tell(), "PartTablePointer"))
            write_int(0, file)
            
            targets.append(PointerTarget(file.tell(), "PartTablePointer"))
            count = 0
            for part in parts:
                print(part.fe14_props.name)
                
                # Name
                pointers.append(Pointer(file.tell(), part.fe14_props.name))
                write_int(0, file)
                
                # BCH Name
                pointers.append(Pointer(file.tell(), part.fe14_props.file_name))
                write_int(0, file)
                
                # Type
                if part.fe14_props.part_type == 'GROUND':
                    write_int(0, file)
                if part.fe14_props.part_type == 'MAP OBJECT':
                    write_int(2, file)
                if part.fe14_props.part_type == 'ANANKOS':
                    write_int(4, file)
                    
                for val in part.fe14_props.part_extents_1:
                    #write_float(val, file)
                    write_float(0, file)
                for val in part.fe14_props.part_extents_2:
                    #write_float(val, file)
                    write_float(100, file)
                
                # Visibility Flags(?)
                flags = bytearray([ part.fe14_props.part_flags_1, part.fe14_props.part_flags_2, part.fe14_props.part_flags_3, part.fe14_props.part_flags_4 ])
                immutable = bytes(flags)
                file.write(immutable)
                
                # Weird Floats
                bar = 0
                while bar < 4:
                    foo = 0
                    while foo < 3:
                        write_float(1, file)
                        foo+=1
                    foo = 0
                    while foo < 6:
                        write_float(0, file)
                        foo+=1
                    
                    bar+=1
                    
                # Pointers
                # 3 height, 6 collision, 6 effects, 1 mycastle offset
                
                # Height
                if part.fe14_props.part_height_1 != "":
                    if count > 0:
                        pointers.append(Pointer(file.tell(), part.fe14_props.part_height_1))
                    else:
                        pointers.insert(1, Pointer(file.tell(), part.fe14_props.part_height_1))
                write_int(0, file)
                
                if part.fe14_props.part_height_2 != "":
                    if count > 0:
                        pointers.append(Pointer(file.tell(), part.fe14_props.part_height_2))
                    else:
                        pointers.insert(2, Pointer(file.tell(), part.fe14_props.part_height_2))
                write_int(0, file)
                
                if part.fe14_props.part_height_3 != "":
                    if count > 0:
                        pointers.append(Pointer(file.tell(), part.fe14_props.part_height_3))
                    else:
                        pointers.insert(3, Pointer(file.tell(), part.fe14_props.part_height_3))
                        
                write_int(0, file)
                
                # Collision
                if part.fe14_props.part_collision_1 != "":
                    pointers.append(Pointer(file.tell(), part.fe14_props.part_collision_1))
                write_int(0, file)
                if part.fe14_props.part_collision_2 != "":
                    pointers.append(Pointer(file.tell(), part.fe14_props.part_collision_2))
                write_int(0, file)
                if part.fe14_props.part_collision_3 != "":
                    pointers.append(Pointer(file.tell(), part.fe14_props.part_collision_3))
                write_int(0, file)
                if part.fe14_props.part_collision_4 != "":
                    pointers.append(Pointer(file.tell(), part.fe14_props.part_collision_4))
                write_int(0, file)
                if part.fe14_props.part_collision_5 != "":
                    pointers.append(Pointer(file.tell(), part.fe14_props.part_collision_5))
                write_int(0, file)
                if part.fe14_props.part_collision_6 != "":
                    pointers.append(Pointer(file.tell(), part.fe14_props.part_collision_6))
                write_int(0, file)
                
                # Effect
                foo = 0
                while foo < 7:
                    write_int(0, file)
                    foo += 1
                    
                count += 1
            
            # STEP 3: REFERS
            
            targets.append(PointerTarget(file.tell(), "ReferCountPointer"))
            write_int(len(refers), file)
            pointers.append(Pointer(file.tell(), "ReferTablePointer"))
            write_int(0, file)
            
            targets.append(PointerTarget(file.tell(), "ReferTablePointer"))
            for refer in refers:
                # Name
                pointers.append(Pointer(file.tell(), refer.fe14_props.name))
                write_int(0, file)
                
                # Name in model file
                pointers.append(Pointer(file.tell(), refer.fe14_props.file_name))
                write_int(0, file)
                
                # Transforms
                # We need to convert from Z up Y right X forward to
                # Y up X right Z forward
                
                transformed_scale = refer.scale.yzx
                transformed_rotation = refer.rotation_euler.copy()
                transformed_rotation.order = 'YZX'
                transformed_position = refer.location.yzx
                transformed_position.y *= -1
                
                for val in transformed_scale:
                    write_float(val, file)
                for val in transformed_rotation:
                    write_float(val, file)
                for val in transformed_position:
                    write_float(val, file)
            
            # STEP 4: FILES
            targets.append(PointerTarget(file.tell(), "FileCountPointer"))
            write_int(len(files), file)
            pointers.append(Pointer(file.tell(), "FileTablePointer"))
            write_int(0, file)
            
            targets.append(PointerTarget(file.tell(), "FileTablePointer"))
            for f in files:
                pointers.append(Pointer(file.tell(), f))
                write_int(0, file)
            
            # STEP 5: EFFECTS
            # Dummied out because I dont use these and dont want to
            
            # STEP 6: HEIGHTS
            # I hate how these are backwards
            
            for height in heights:
                bm = bmesh.new()
                bm.from_mesh(height.data)
                
                # tracking for bounding box
                lowest = mathutils.Vector((0.0, 0.0, 0.0))
                highest = mathutils.Vector((0.0, 0.0, 0.0))
                
                targets.append(PointerTarget(file.tell(), height.name+"Start"))
                
                for face in bm.faces:
                    type1 = 0
                    type2 = 1
                    loop = 0
                    
                    while loop < 2:
                    
                        pos = face.calc_center_bounds()
                        # Normalize to per-tile coordinates
                        pos.y *= -1
                        pos.xy /= 50.0
                        pos -= mathutils.Vector((0.4999, 0.4999, 0.0))
                        
                        #print(pos)
                        
                        # Write tile location
                        write_char(int(pos.x), file)
                        write_char(int(pos.y), file)
                        
                        # update bounding box
                        if pos.x * 50 < lowest.x:
                            lowest.x = pos.x * 50
                        if pos.y * 50 < lowest.y:
                            lowest.y = pos.y * 50
                            
                        if pos.x * 50 > highest.x:
                            highest.x = pos.x * 50
                        if pos.y * 50 > highest.y:
                            highest.y = pos.y * 50
                        
                        # Type
                        write_char(type1, file)
                        write_char(type2, file)
                        
                        #write_short(int(face.verts[3].co.z * 16), file)
                        #write_short(int(face.verts[0].co.z * 16), file)
                        #write_short(int(face.verts[2].co.z * 16), file)
                        #write_short(int(face.verts[1].co.z * 16), file)
                        
                        height_list = [0.0, 0.0, 0.0, 0.0]
                        
                        # strategy: normalize
                        
                        for vert in face.verts:
                            # THIS RUNS TWICE. Dont overwrite the original data.
                            #vert.co.xy /= 50.0
                            
                            temp_co = vert.co.copy()
                            temp_co.xy /= 50.0
                            temp_co.y *= -1
                            #vert.co -= mathutils.Vector((0.5, 0.5, 0.0))
                            #print(temp_co)
                            
                            # Now that we've put them in the same coord system as the tiles, can figure out
                            # which corner is which.
                            
                            success = False
                            
                            temp_x = int(round(temp_co.x))
                            temp_y = int(round(temp_co.y))
                            temp_p_x = int(round(pos.x))
                            temp_p_y = int(round(pos.y))
                            
                            if temp_x == temp_p_x and temp_y == temp_p_y:
                                height_list[0] = vert.co.z*16
                                success = True
                            if temp_x == temp_p_x and temp_y > temp_p_y:
                                height_list[1] = vert.co.z*16
                                success = True
                            if temp_x > temp_p_x and temp_y == temp_p_y:
                                height_list[2] = vert.co.z*16
                                success = True
                            if temp_x > temp_p_x and temp_y > temp_p_y:
                                height_list[3] = vert.co.z*16
                                success = True
                            
                            '''
                            #if math.isclose(temp_co.x, pos.x, abs_tol=0.2) and math.isclose(temp_co.y, pos.y, abs_tol=0.2):
                            #    #print("1 TOP LEFT")
                            #    height_list[0] = vert.co.z*16
                            #    success = True
                            elif math.isclose(temp_co.x, pos.x, abs_tol=0.2) and temp_co.y > pos.y:
                                #print("2 BOTTOM LEFT")
                                height_list[1] = vert.co.z*16
                                success = True
                            elif temp_co.x > pos.x and math.isclose(temp_co.y, pos.y, abs_tol=0.2):
                                #print("3 TOP RIGHT")
                                height_list[2] = vert.co.z*16
                                success = True
                            elif temp_co.x > pos.x and temp_co.y > pos.y:
                                #print("4 BOTTOM RIGHT")
                                height_list[3] = vert.co.z*16
                                success = True
                            '''
                            if success == False:
                                print("FAILED VERT")
                                print(temp_co)
                                print(str(temp_co.x))
                                print(str(temp_co.y))
                                print("FAILED TILE")
                                print(pos)
                                print(str(pos.x))
                                print(str(pos.y))
                                
                        print(height_list)
                        for val in height_list:
                            write_short(int(val), file)
                            #write_short(int(pos.z*16), file)
                        
                        '''
                        for vert in face.verts:
                            #write_short(800, file)
                            swizzle = vert.co.yzx
                            val = swizzle.y
                            if val < lowest.z:
                                lowest.z = val
                            if val > highest.z:
                                highest.z = val
                            write_short(int(val * 16), file)
                        '''
                        loop +=1
                        type1 = 1
                         
                # Write header
                targets.append(PointerTarget(file.tell(), height.name))
                write_int(len(bm.faces)*2, file)
                # stupid pointer
                pointers.append(Pointer(file.tell(), height.name+"Start"))
                write_int(0, file)
                # bounding box/extents
                for val in lowest:
                    #write_float(val, file)
                    write_float(-20000, file)
                for val in highest:
                    #write_float(val, file)
                    write_float(20000, file)
                
            # STEP 7: COLLISIONS
            print("COLLISION COUNT " + str(len(collisions)))
            
            for collision in collisions:
                bm = bmesh.new()
                bm.from_mesh(collision.data)
                #bmesh.ops.triangulate(bm)
                
                # tracking for bounding box
                lowest = mathutils.Vector((-20000.0, -20000.0, -20000.0))
                highest = mathutils.Vector((20000.0, 20000.0, 20000.0))
                
                targets.append(PointerTarget(file.tell(), collision.name+"Start"))
                
                # dave help me
                for face in bm.faces:
                    for vert in face.verts:
                        swizzle = vert.co.yzx
                        swizzle.y *= -1
                        #print(swizzle)
                        write_short(int(swizzle.x * 16), file)
                        write_short(int(swizzle.y * 16), file)
                        write_short(int(swizzle.z * 16), file)
                        #for coord in swizzle:
                        #    write_short(int(coord * 16), file)
                # mystery short(probably grass controller or smth)
                write_short(0, file)
                
                #For unknown reasons, the file pointer wont advance properly here.
                file.seek(file.tell()+2)
                
                # Write header
                targets.append(PointerTarget(file.tell(), collision.name))
                write_int(len(bm.faces), file)
                print("Face count: " + str(len(bm.faces)))
                # stupid pointer
                pointers.append(Pointer(file.tell(), collision.name+"Start"))
                write_int(0, file)
                # bounding box/extents
                for val in lowest:
                    write_float(val, file)
                for val in highest:
                    write_float(val, file)
            
            # STEP 8: THAT POINTER LIST THAT I HATE
            print(pointers)
            
            pointerListPosition = file.tell()
            
            # SOME POINTERS MUST COME FIRST!!!
            # 0c 00: PartTablePointer
            # c8 00: first Part's first map height pointer
            # cc 00: first Part's second map height pointer
            # d0 00: first Part's third map height pointer
            # 0c 01: ReferTablePointer - prob not
            
            for pointer in pointers:
                write_int(pointer.pos-32, file)
            
            # STEP 9: MISC DATA
            write_int(0, file)
            write_int(0, file)
            
            pointers.append(Pointer(file.tell(), "PartCountPointer"))
            write_int(0, file)
            write_int(10, file)
            pointers.append(Pointer(file.tell(), "ReferCountPointer"))
            write_int(0, file)
            write_int(20, file)
            pointers.append(Pointer(file.tell(), "FileCountPointer"))
            write_int(0, file)
            write_int(30, file)
            
            # STEP 10: STRINGS
            print(strings)
            
            file.write(b"MapHeader\0")
            file.write(b"PartsList\0")
            file.write(b"ReferList\0")
            file.write(b"FileList\0")
            
            for string in strings:
                targets.append(PointerTarget(file.tell(), string))
                file.write(bytes(string + "\0", 'ascii'))
            
            #for f in files:
            #    targets.append(PointerTarget(file.tell(), string))
            #    file.write(bytes(string + "\0", 'ascii'))
            
        # Pass 2
        
        with open(self.filepath, 'r+b') as file:
            # Write file length
            write_int(os.path.getsize(self.filepath), file)
            file.seek(4)
            write_int(pointerListPosition-32, file)
            file.seek(8)
            # Write pointer count
            write_int(len(pointers)-3, file)
            #print(pointers)
            print(str(len(pointers)-3))
            
            # Resolve Pointers
            for pointer in pointers:
                # god help me
                for target in targets:
                    if target.name == pointer.target:
                        file.seek(pointer.pos)
                        write_int(target.pos-32, file)
            
        return {'FINISHED'}

def write_int(value, file):
    file.write(struct.pack("<i", value))

def write_short(value, file):
    file.write(struct.pack("<h", value))

def write_char(value, file):
    file.write(struct.pack("<b", value))

def write_float(value, file):
    file.write(struct.pack("<f", value))
    
classes = [
    ImportField,
    ExportField
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == '__main__':
    register()