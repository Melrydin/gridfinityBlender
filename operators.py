import bpy
from . import geometry

class GRIDFINITY_OT_create_container(bpy.types.Operator):
    """Create a new Gridfinity container base unit restricted to 4.75mm height"""
    bl_idname = "gridfinity.create_container"
    bl_label = "Create Gridfinity Base"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        nx = context.scene.gridfinity_x
        ny = context.scene.gridfinity_y

        obj = geometry.create_container_mesh(context)

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

        self.report({'INFO'}, "Gridfinity container unit created with exactly 4.75mm height.")
        return {'FINISHED'}

class GRIDFINITY_OT_create_box(bpy.types.Operator):
    """Create a new Gridfinity box on top of the baseplate with inner bottom bevel"""
    bl_idname = "gridfinity.create_box"
    bl_label = "Create Gridfinity Box"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        nx = context.scene.gridfinity_x
        ny = context.scene.gridfinity_y
        height_mm = context.scene.gridfinity_box_height
        thickness_mm = context.scene.gridfinity_box_thickness

        geometry.create_box_mesh(context, nx, ny, height_mm, thickness_mm)

        self.report({'INFO'}, "Gridfinity box with inner bottom bevel created.")
        return {'FINISHED'}


class GRIDFINITY_OT_create_solid_box(bpy.types.Operator):
    """Create a solid Gridfinity box with a 2mm top rim and inner bottom bevel"""
    bl_idname = "gridfinity.create_solid_box"
    bl_label = "Create Solid Box"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        nx = context.scene.gridfinity_x
        ny = context.scene.gridfinity_y
        height_mm = context.scene.gridfinity_box_height
        thickness_mm = context.scene.gridfinity_box_thickness

        geometry.create_solid_box_mesh(context, nx, ny, height_mm, thickness_mm)

        self.report({'INFO'}, "Solid Gridfinity box with 2mm rim and inner bevel created.")
        return {'FINISHED'}

class GRIDFINITY_OT_create_basegrid(bpy.types.Operator):
    """Full Gridfinity base profile generation with closed manifold bottom"""
    bl_idname = "gridfinity.create_basegrid"
    bl_label = "Create Basegrid"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        geometry.create_basegrid_mesh(context)

        self.report({'INFO'}, "Gridfinity Basegrid perfectly hollowed and bridged.")
        return {'FINISHED'}


class GRIDFINITY_OT_create_container_with_box(bpy.types.Operator):
    """Create a Gridfinity container with a hollow box on top"""
    bl_idname = "gridfinity.create_container_with_box"
    bl_label = "Container + Hollow Box"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        nx = context.scene.gridfinity_x
        ny = context.scene.gridfinity_y
        height_mm = context.scene.gridfinity_box_height
        thickness_mm = context.scene.gridfinity_box_thickness

        # Constants for sizing
        unit_size = 0.0415
        spacing = 0.001
        pitch = unit_size + spacing  # 0.0425

        # Create container
        obj = geometry.create_container_mesh(context)

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

        # Create box
        geometry.create_box_mesh(context, nx, ny, height_mm, thickness_mm)

        self.report({'INFO'}, "Container with hollow box created.")
        return {'FINISHED'}


class GRIDFINITY_OT_create_container_with_solid_box(bpy.types.Operator):
    """Create a Gridfinity container with a solid box on top"""
    bl_idname = "gridfinity.create_container_with_solid_box"
    bl_label = "Container + Solid Box"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        nx = context.scene.gridfinity_x
        ny = context.scene.gridfinity_y
        height_mm = context.scene.gridfinity_box_height
        thickness_mm = context.scene.gridfinity_box_thickness

        # Constants for sizing
        unit_size = 0.0415
        spacing = 0.001
        pitch = unit_size + spacing  # 0.0425

        # Create container
        obj = geometry.create_container_mesh(context)

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

        # Create solid box
        geometry.create_solid_box_mesh(context, nx, ny, height_mm, thickness_mm)

        self.report({'INFO'}, "Container with solid box created.")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(GRIDFINITY_OT_create_container)
    bpy.utils.register_class(GRIDFINITY_OT_create_box)
    bpy.utils.register_class(GRIDFINITY_OT_create_solid_box)
    bpy.utils.register_class(GRIDFINITY_OT_create_basegrid)
    bpy.utils.register_class(GRIDFINITY_OT_create_container_with_box)
    bpy.utils.register_class(GRIDFINITY_OT_create_container_with_solid_box)


def unregister():
    bpy.utils.unregister_class(GRIDFINITY_OT_create_container)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_box)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_solid_box)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_basegrid)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_container_with_box)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_container_with_solid_box)
