import bpy
from . import geometry
import math
import mathutils


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

        obj = geometry.create_bin_mesh(context, nx, ny, height_mm, thickness_mm)
        obj.name = f"Gridfinity_Box_{nx}x{ny}_H{int(height_mm)}"

        geometry.center_origin_to_bounds(context, obj)

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

        obj = geometry.create_solid_bin_mesh(context, nx, ny, height_mm, thickness_mm)

        geometry.center_origin_to_bounds(context, obj)

        self.report({'INFO'}, "Solid Gridfinity bin with 2mm rim and inner bevel created.")
        return {'FINISHED'}


class GRIDFINITY_OT_create_stacking_lip(bpy.types.Operator):
    """Full Gridfinity stacking lip profile generation with closed manifold bottom"""
    bl_idname = "gridfinity.create_stacking_lip"
    bl_label = "Create Stacking Lip"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = geometry.create_stacking_lip_mesh(context)

        geometry.center_origin_to_bounds(context, obj)

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
        obj.name = f"Gridfinity_Baseplate_{nx}x{ny}"

        geometry.center_origin_to_bounds(context, obj)

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
        bin_obj = geometry.create_bin_mesh(context, nx, ny, height_mm, thickness_mm)
        obj.name = f"Gridfinity_Baseplate_{nx}x{ny}"
        bin_obj.name = f"Gridfinity_Complete_Box_{nx}x{ny}_H{int(height_mm)}"

        geometry.center_origin_to_bounds(context, obj)
        geometry.center_origin_to_bounds(context, bin_obj)

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
        bin_obj = geometry.create_solid_bin_mesh(context, nx, ny, height_mm, thickness_mm)
        obj.name = f"Gridfinity_Baseplate_{nx}x{ny}"
        bin_obj.name = f"Gridfinity_Complete_SolidBox_{nx}x{ny}_H{int(height_mm)}"

        geometry.center_origin_to_bounds(context, obj)
        geometry.center_origin_to_bounds(context, bin_obj)

        self.report({'INFO'}, "Gridfinity baseplate with solid bin created.")
        return {'FINISHED'}


class GRIDFINITY_OT_create_stacking_lip_array(bpy.types.Operator):
    """Generate grid array using Marching Squares neighbor logic with debug grid"""
    bl_idname = "gridfinity.create_stacking_lip_array"
    bl_label = "Create Stacking Lip Array"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        nx = context.scene.gridfinity_x
        ny = context.scene.gridfinity_y

        pitch = 0.042

        obj_l = geometry.load_reference_object(context, "baseplate_L.obj")
        obj_t = geometry.load_reference_object(context, "baseplate_T.obj")
        obj_x = geometry.load_reference_object(context, "baseplate_X.obj")

        if not obj_l or not obj_t or not obj_x:
            self.report({'ERROR'}, "OBJ files missing")
            return {'CANCELLED'}

        grid = [[True for _ in range(ny)] for _ in range(nx)]

        def cell_exists(cx, cy):
            if 0 <= cx < nx and 0 <= cy < ny:
                return grid[cx][cy]
            return False

        array_parts = []

        for x in range(nx + 1):
            for y in range(ny + 1):
                tr = cell_exists(x, y)
                tl = cell_exists(x - 1, y)
                bl = cell_exists(x - 1, y - 1)
                br = cell_exists(x, y - 1)

                state = (tr, tl, bl, br)

                source_obj = None
                rotation_z = 0.0

                if state == (True, False, False, False):
                    source_obj = obj_l
                    rotation_z = math.radians(180)
                elif state == (False, True, False, False):
                    source_obj = obj_l
                    rotation_z = math.radians(-90)
                elif state == (False, False, True, False):
                    source_obj = obj_l
                    rotation_z = math.radians(0)
                elif state == (False, False, False, True):
                    source_obj = obj_l
                    rotation_z = math.radians(90)
                elif state == (True, True, False, False):
                    source_obj = obj_t
                    rotation_z = math.radians(180)
                elif state == (False, True, True, False):
                    source_obj = obj_t
                    rotation_z = math.radians(-90)
                elif state == (False, False, True, True):
                    source_obj = obj_t
                    rotation_z = math.radians(0)
                elif state == (True, False, False, True):
                    source_obj = obj_t
                    rotation_z = math.radians(90)
                elif state == (True, True, True, True):
                    source_obj = obj_x
                    rotation_z = math.radians(0)
                elif state == (False, False, False, False):
                    continue

                if source_obj:
                    new_obj = source_obj.copy()
                    new_obj.data = source_obj.data.copy()
                    context.collection.objects.link(new_obj)

                    new_obj.location = (x * pitch, y * pitch, 0.0)
                    new_obj.rotation_euler = (0.0, 0.0, rotation_z)

                    array_parts.append(new_obj)

        bpy.data.objects.remove(obj_l, do_unlink=True)
        bpy.data.objects.remove(obj_t, do_unlink=True)
        bpy.data.objects.remove(obj_x, do_unlink=True)

        if not array_parts:
            return {'CANCELLED'}

        bpy.ops.object.select_all(action='DESELECT')
        for part in array_parts:
            part.select_set(True)

        context.view_layer.objects.active = array_parts[0]
        bpy.ops.object.join()

        final_obj = context.active_object
        final_obj.name = f"Gridfinity_Lip_Array_{nx}x{ny}"

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=0.0001)
        bpy.ops.object.mode_set(mode='OBJECT')

        geometry.center_origin_to_bounds(context, final_obj)

        self.report({'INFO'}, f"Merged array {nx}x{ny} generated successfully")
        return {'FINISHED'}


class GRIDFINITY_OT_create_drawer_fitted_grid(bpy.types.Operator):
    """Creates a grid and cuts it to the exact drawer dimensions"""
    bl_idname = "gridfinity.create_drawer_fitted_grid"
    bl_label = "Create Fitted Drawer Grid"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        drawer_x = context.scene.gridfinity_drawer_x
        drawer_y = context.scene.gridfinity_drawer_y
        pitch = 42.0

        nx = int((drawer_x / pitch) + 1)
        ny = int((drawer_y / pitch) + 1)

        old_x = context.scene.gridfinity_x
        old_y = context.scene.gridfinity_y
        context.scene.gridfinity_x = nx
        context.scene.gridfinity_y = ny

        bpy.ops.gridfinity.create_stacking_lip_array()

        grid_obj = context.active_object

        context.scene.gridfinity_x = old_x
        context.scene.gridfinity_y = old_y

        bpy.ops.mesh.primitive_cube_add(size=1.0)
        cutter = context.active_object
        cutter.name = "Drawer_Cutter_Temp"

        # Erweitere den Cutter um 10mm in den negativen Bereich, um Z-Fighting zu verhindern.
        # Die positiven Kanten schließen exakt mit drawer_x und drawer_y ab.
        size_x = (drawer_x * 0.001) + 1.0
        size_y = (drawer_y * 0.001) + 1.0
        size_z = 1.0

        cutter.scale = (size_x, size_y, size_z)

        # Position berechnen: Min=-10.0, Max=drawer_x
        cutter.location.x = ((drawer_x * 0.001)  - 1.0) / 2.0
        cutter.location.y = ((drawer_y * 0.001) - 1.0) / 2.0
        cutter.location.z = 0.0

        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        context.view_layer.objects.active = grid_obj
        bool_mod = grid_obj.modifiers.new(name="Drawer_Cut", type='BOOLEAN')
        bool_mod.operation = 'INTERSECT'
        bool_mod.object = cutter
        bool_mod.solver = 'EXACT'

        bpy.ops.object.modifier_apply(modifier="Drawer_Cut")

        bpy.data.objects.remove(cutter, do_unlink=True)

        geometry.center_origin_to_bounds(context, grid_obj)

        self.report({'INFO'}, f"Grid fitted to {drawer_x}mm x {drawer_y}mm")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(GRIDFINITY_OT_create_baseplate)
    bpy.utils.register_class(GRIDFINITY_OT_create_bin)
    bpy.utils.register_class(GRIDFINITY_OT_create_solid_bin)
    bpy.utils.register_class(GRIDFINITY_OT_create_stacking_lip)
    bpy.utils.register_class(GRIDFINITY_OT_create_baseplate_with_bin)
    bpy.utils.register_class(GRIDFINITY_OT_create_baseplate_with_solid_bin)
    bpy.utils.register_class(GRIDFINITY_OT_create_stacking_lip_array)
    bpy.utils.register_class(GRIDFINITY_OT_create_drawer_fitted_grid)


def unregister():
    bpy.utils.unregister_class(GRIDFINITY_OT_create_baseplate)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_bin)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_solid_bin)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_stacking_lip)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_baseplate_with_bin)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_baseplate_with_solid_bin)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_stacking_lip_array)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_drawer_fitted_grid)
