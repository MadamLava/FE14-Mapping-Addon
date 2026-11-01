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
        def __init__(self, name="", filename="", type=0, offset_x=0, offset_y=0, offset_z=0, extent_x=0, extent_y=0, extent_z=0, flags=0, map_height=[], collision=[], effects=[], shop_offset=None):
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