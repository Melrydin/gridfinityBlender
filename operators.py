import bpy
from . import geometry

class GRIDFINITY_OT_create_bin(bpy.types.Operator):
    """Create a hollow Gridfinity bin on top of the baseplate with inner bottom bevel"""
    bl_idname = "gridfinity.create_bin"
    bl_label = "Create Gridfinity Bin"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        nx = context.scene.gridfinity_x
        ny = context.scene.gridfinity_y
        height_mm = context.scene.gridfinity_bin_height
        thickness_mm = context.scene.gridfinity_bin_wall_thickness

        geometry.create_bin_mesh(context, nx, ny, height_mm, thickness_mm)

        self.report({'INFO'}, "Gridfinity bin with inner bottom bevel created.")
        return {'FINISHED'}


class GRIDFINITY_OT_create_solid_bin(bpy.types.Operator):
    """Create a solid Gridfinity bin with a 2mm top rim and inner bottom bevel"""
    bl_idname = "gridfinity.create_solid_bin"
    bl_label = "Create Solid Bin"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        nx = context.scene.gridfinity_x
        ny = context.scene.gridfinity_y
        height_mm = context.scene.gridfinity_bin_height
        thickness_mm = context.scene.gridfinity_bin_wall_thickness

        geometry.create_solid_bin_mesh(context, nx, ny, height_mm, thickness_mm)

        self.report({'INFO'}, "Solid Gridfinity bin with 2mm rim and inner bevel created.")
        return {'FINISHED'}


class GRIDFINITY_OT_create_stacking_lip(bpy.types.Operator):
    """Full Gridfinity stacking lip profile generation with closed manifold bottom"""
    bl_idname = "gridfinity.create_stacking_lip"
    bl_label = "Create Stacking Lip"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        geometry.create_stacking_lip_mesh(context)

        self.report({'INFO'}, "Gridfinity stacking lip perfectly hollowed and bridged.")
        return {'FINISHED'}


class GRIDFINITY_OT_create_baseplate(bpy.types.Operator):
    """Create a Gridfinity baseplate unit restricted to 4.75mm height"""
    bl_idname = "gridfinity.create_baseplate"
    bl_label = "Create Gridfinity Baseplate"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        nx = context.scene.gridfinity_x
        ny = context.scene.gridfinity_y

        obj = geometry.create_baseplate_unit_mesh(context)

        # Constants for sizing
        unit_size = 0.0415
        spacing = 0.001
        pitch = unit_size + spacing  # 0.0425

        # Apply array modifiers for tiling
        if nx > 1:
            mod_x = obj.modifiers.new(name="Array_X", type='ARRAY')
            mod_x.count = nx
            mod_x.use_relative_offset = False
            mod_x.use_constant_offset = True
            mod_x.constant_offset_displace = (pitch, 0.0, 0.0)
            mod_x.use_merge_vertices = True
            mod_x.merge_threshold = 0.0001
            bpy.ops.object.modifier_apply(modifier="Array_X")

        if ny > 1:
            mod_y = obj.modifiers.new(name="Array_Y", type='ARRAY')
            mod_y.count = ny
            mod_y.use_relative_offset = False
            mod_y.use_constant_offset = True
            mod_y.constant_offset_displace = (0.0, pitch, 0.0)
            mod_y.use_merge_vertices = True
            mod_y.merge_threshold = 0.0001
            bpy.ops.object.modifier_apply(modifier="Array_Y")

        # Center the entire object around origin
        offset_x = -(nx - 1) * pitch / 2.0
        offset_y = -(ny - 1) * pitch / 2.0
        obj.location.x += offset_x
        obj.location.y += offset_y

        self.report({'INFO'}, "Gridfinity baseplate created with exactly 4.75mm height.")
        return {'FINISHED'}


class GRIDFINITY_OT_create_baseplate_with_bin(bpy.types.Operator):
    """Create a Gridfinity baseplate with a hollow bin on top"""
    bl_idname = "gridfinity.create_baseplate_with_bin"
    bl_label = "Baseplate + Hollow Bin"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        nx = context.scene.gridfinity_x
        ny = context.scene.gridfinity_y
        height_mm = context.scene.gridfinity_bin_height
        thickness_mm = context.scene.gridfinity_bin_wall_thickness

        # Constants for sizing
        unit_size = 0.0415
        spacing = 0.001
        pitch = unit_size + spacing  # 0.0425

        # Create baseplate
        obj = geometry.create_baseplate_unit_mesh(context)

        # Apply array modifiers for tiling
        if nx > 1:
            mod_x = obj.modifiers.new(name="Array_X", type='ARRAY')
            mod_x.count = nx
            mod_x.use_relative_offset = False
            mod_x.use_constant_offset = True
            mod_x.constant_offset_displace = (pitch, 0.0, 0.0)
            mod_x.use_merge_vertices = True
            mod_x.merge_threshold = 0.0001
            bpy.ops.object.modifier_apply(modifier="Array_X")

        if ny > 1:
            mod_y = obj.modifiers.new(name="Array_Y", type='ARRAY')
            mod_y.count = ny
            mod_y.use_relative_offset = False
            mod_y.use_constant_offset = True
            mod_y.constant_offset_displace = (0.0, pitch, 0.0)
            mod_y.use_merge_vertices = True
            mod_y.merge_threshold = 0.0001
            bpy.ops.object.modifier_apply(modifier="Array_Y")

        # Center the entire object around origin
        offset_x = -(nx - 1) * pitch / 2.0
        offset_y = -(ny - 1) * pitch / 2.0
        obj.location.x += offset_x
        obj.location.y += offset_y

        # Create hollow bin
        geometry.create_bin_mesh(context, nx, ny, height_mm, thickness_mm)

        self.report({'INFO'}, "Gridfinity baseplate with hollow bin created.")
        return {'FINISHED'}


class GRIDFINITY_OT_create_baseplate_with_solid_bin(bpy.types.Operator):
    """Create a Gridfinity baseplate with a solid bin on top"""
    bl_idname = "gridfinity.create_baseplate_with_solid_bin"
    bl_label = "Baseplate + Solid Bin"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        nx = context.scene.gridfinity_x
        ny = context.scene.gridfinity_y
        height_mm = context.scene.gridfinity_bin_height
        thickness_mm = context.scene.gridfinity_bin_wall_thickness

        # Constants for sizing
        unit_size = 0.0415
        spacing = 0.001
        pitch = unit_size + spacing  # 0.0425

        # Create baseplate
        obj = geometry.create_baseplate_unit_mesh(context)

        # Apply array modifiers for tiling
        if nx > 1:
            mod_x = obj.modifiers.new(name="Array_X", type='ARRAY')
            mod_x.count = nx
            mod_x.use_relative_offset = False
            mod_x.use_constant_offset = True
            mod_x.constant_offset_displace = (pitch, 0.0, 0.0)
            mod_x.use_merge_vertices = True
            mod_x.merge_threshold = 0.0001
            bpy.ops.object.modifier_apply(modifier="Array_X")

        if ny > 1:
            mod_y = obj.modifiers.new(name="Array_Y", type='ARRAY')
            mod_y.count = ny
            mod_y.use_relative_offset = False
            mod_y.use_constant_offset = True
            mod_y.constant_offset_displace = (0.0, pitch, 0.0)
            mod_y.use_merge_vertices = True
            mod_y.merge_threshold = 0.0001
            bpy.ops.object.modifier_apply(modifier="Array_Y")

        # Center the entire object around origin
        offset_x = -(nx - 1) * pitch / 2.0
        offset_y = -(ny - 1) * pitch / 2.0
        obj.location.x += offset_x
        obj.location.y += offset_y

        # Create solid bin
        geometry.create_solid_bin_mesh(context, nx, ny, height_mm, thickness_mm)

        self.report({'INFO'}, "Gridfinity baseplate with solid bin created.")
        return {'FINISHED'}


class GRIDFINITY_OT_create_stacking_lip_array(bpy.types.Operator):
    """Create a Stacking Lip Array merged into a single mesh"""
    bl_idname = "gridfinity.create_lip_array"
    bl_label = "Create Stacking Lip Array"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        nx = context.scene.gridfinity_x
        ny = context.scene.gridfinity_y

        # Ruft deine Mesh-Funktion auf (muss ein Blender Object zurückgeben)
        obj = geometry.create_stacking_lip_mesh(context)

        # Gridfinity Standard Pitch (42mm)
        pitch = 0.042

        # X-Array anwenden
        if nx > 1:
            mod_x = obj.modifiers.new(name="Array_X", type='ARRAY')
            mod_x.count = nx
            mod_x.use_relative_offset = False
            mod_x.use_constant_offset = True
            mod_x.constant_offset_displace = (pitch, 0.0, 0.0)
            mod_x.use_merge_vertices = True
            mod_x.merge_threshold = 0.0001
            bpy.ops.object.modifier_apply(modifier="Array_X")

        # Y-Array anwenden
        if ny > 1:
            mod_y = obj.modifiers.new(name="Array_Y", type='ARRAY')
            mod_y.count = ny
            mod_y.use_relative_offset = False
            mod_y.use_constant_offset = True
            mod_y.constant_offset_displace = (0.0, pitch, 0.0)
            mod_y.use_merge_vertices = True
            mod_y.merge_threshold = 0.0001
            bpy.ops.object.modifier_apply(modifier="Array_Y")

        # Das gesamte Gitter auf dem Ursprung zentrieren
        offset_x = -(nx - 1) * pitch / 2.0
        offset_y = -(ny - 1) * pitch / 2.0
        obj.location.x += offset_x
        obj.location.y += offset_y

        self.report({'INFO'}, f"Stacking Lip Array ({nx}x{ny}) created.")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(GRIDFINITY_OT_create_baseplate)
    bpy.utils.register_class(GRIDFINITY_OT_create_bin)
    bpy.utils.register_class(GRIDFINITY_OT_create_solid_bin)
    bpy.utils.register_class(GRIDFINITY_OT_create_stacking_lip)
    bpy.utils.register_class(GRIDFINITY_OT_create_baseplate_with_bin)
    bpy.utils.register_class(GRIDFINITY_OT_create_baseplate_with_solid_bin)
    bpy.utils.register_class(GRIDFINITY_OT_create_stacking_lip_array)


def unregister():
    bpy.utils.unregister_class(GRIDFINITY_OT_create_baseplate)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_bin)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_solid_bin)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_stacking_lip)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_baseplate_with_bin)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_baseplate_with_solid_bin)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_stacking_lip_array)
