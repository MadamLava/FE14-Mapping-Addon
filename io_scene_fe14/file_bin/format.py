### Definition for the actual Field BIN format ###

from mathutils import Vector

class Field():
    def __init__(self, filepath=None):
        if filepath:
            self.filepath = filepath
        
        self.parts = []
        self.refers = []
    
    # Defined Parts
    class Part:
        def __init__(self, name="", filename="", type=0, offset_x=10000.0, offset_y=10000.0, offset_z=10000.0, extent_x=-10000.0, extent_y=-10000.0, extent_z=-10000.0, flags=0, map_height=[], collision=[], effects=[], shop_offset=None):
            self.name = name
            self.filename = filename
            self.type = type
            self.offset_x = offset_x
            self.offset_y = offset_y
            self.offset_z = offset_z
            self.extent_x = extent_x
            self.extent_y = extent_y
            self.extent_z = extent_z
            self.flags = flags
            self.map_height = map_height
            self.collision = collision
            self.effects = effects
            self.shop_offset = shop_offset
    
    # Components that are nothing but a named position (Refers, Effects, MyCastle Offset)
    class Transform:
        def __init__(self, name="", filename="", scale=Vector(), rotation=Vector(), translation=Vector()):
            self.name = name
            self.filename = filename
            self.scale = scale
            self.rotation = rotation
            self.translation = translation

def read_u32(f):
    return int.from_bytes(f.read(4), byteorder='little')

def read_float(f):
    return float.from_bytes(f.read(4), byteorder='little')

def import_field(filepath):
    field = Field()
    f = open(filepath, "rb")
    
    
    # Read Map Header
    offset = 0
    f.seek(0)
    
    file_length = read_u32(f)
    offset += 4
    f.seek(offset)
    pointer_list_pointer = read_u32(f)
    offset += 4
    f.seek(offset)
    pointer_count = read_u32(f)
    offset += 24
    f.seek(offset)
    map_name_pointer = read_u32(f)
    offset += 4
    f.seek(offset)
    part_count = read_u32(f)
    
    if part_count == 0:
        print("Field has 0 Parts")
        
    
    offset += 4
    f.seek(offset)
    part_table_pointer = read_u32(f)
    
    offset = part_table_pointer + 32
    f.seek(offset)
    
    # Process Parts
    i = 0
    while i < part_count:
        part_name_pointer = read_u32(f)
        f.seek(part_name_pointer + 32)
        part_name = str.from_bytes()
        offset += 4
        f.seek(offset)
        part_filename_pointer = read_u32(f)
        f.seek(part_filename_pointer + 32)
        part_filename = str.from_bytes()
        offset += 4
        f.seek(offset)
        part_type = read_u32(f)
        
        offset += 28
        f.seek(offset)
        
        part_flags = read_u32(f)
        
        offset += 144
        f.seek(offset)
        
        i=0
        part_map_height_pointers = []
        while i < 3:
            part_map_height_pointers.append(read_u32(f))
            
            offset += 4
            f.seek(offset)
            
            i+=1
        
        i=0
        part_collision_pointers = []
        while i < 6:
            part_collision_pointers.append(read_u32(f))
            
            offset += 4
            f.seek(offset)
            
            i+=1
            
        i=0
        part_effect_pointers = []
        while i < 6:
            part_effect_pointers.append(read_u32(f))
            
            offset += 4
            f.seek(offset)
            
            i+=1
        
        part_shop_offset_pointer = read_u32(f)
        
        
        
        part = Part(
            part_name, 
            part_filename,
            part_type,
            10000.0,
            10000.0,
            10000.0,
            -10000.0,
            -10000.0,
            -10000.0,
            part_flags
            
        )
        
        i+=1
    
    return field