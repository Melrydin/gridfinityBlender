import bpy
from . import geometry
import bmesh
import math

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
    """Create a Stacking Lip Array merged into a single mesh"""
    bl_idname = "gridfinity.create_lip_array"
    bl_label = "Create Stacking Lip Array"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        nx = context.scene.gridfinity_x
        ny = context.scene.gridfinity_y
        pitch = 0.042

        obj = geometry.create_stacking_lip_mesh(context)
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        edges_to_delete = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 0.003]
        bmesh.ops.delete(bm, geom=edges_to_delete, context='EDGES')
        bm.to_mesh(obj.data)
        bm.free()

        if nx > 1:
            mod_x = obj.modifiers.new(name="Array_X", type='ARRAY')
            mod_x.count = nx
            mod_x.use_relative_offset = False
            mod_x.use_constant_offset = True
            mod_x.constant_offset_displace = (pitch, 0.0, 0.0)
            mod_x.use_merge_vertices = True
            mod_x.merge_threshold = 0.00001
            bpy.ops.object.modifier_apply(modifier="Array_X")

        if ny > 1:
            mod_y = obj.modifiers.new(name="Array_Y", type='ARRAY')
            mod_y.count = ny
            mod_y.use_relative_offset = False
            mod_y.use_constant_offset = True
            mod_y.constant_offset_displace = (0.0, pitch, 0.0)
            mod_y.use_merge_vertices = True
            mod_y.merge_threshold = 0.00001
            bpy.ops.object.modifier_apply(modifier="Array_Y")

        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.edges.ensure_lookup_table()

        boundary_edges = [e for e in bm.edges if e.is_boundary]

        edge_loops = []
        remaining_edges = set(boundary_edges)

        while remaining_edges:
            edge = remaining_edges.pop()
            loop = [edge]

            for i in range(2):
                current_v = edge.verts[i]
                while True:
                    next_edge = None
                    for connected_edge in current_v.link_edges:
                        if connected_edge in remaining_edges:
                            next_edge = connected_edge
                            break
                    if next_edge:
                        loop.append(next_edge)
                        remaining_edges.remove(next_edge)
                        current_v = next_edge.other_vert(current_v)
                    else:
                        break
            edge_loops.append(loop)

        max_hole_size = 0.035

        for loop in edge_loops:
            verts_in_loop = list(set(v for e in loop for v in e.verts))
            coords = [v.co for v in verts_in_loop]

            min_x = min(c.x for c in coords)
            max_x = max(c.x for c in coords)
            min_y = min(c.y for c in coords)
            max_y = max(c.y for c in coords)

            size_x = max_x - min_x
            size_y = max_y - min_y

            if size_x < max_hole_size and size_y < max_hole_size:
                bmesh.ops.contextual_create(bm, geom=loop)

        bm.edges.ensure_lookup_table()

        boundary_edges = [e for e in bm.edges if e.is_boundary]

        if boundary_edges:
            bmesh.ops.bridge_loops(bm, edges=boundary_edges)

        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

        bm.to_mesh(obj.data)
        bm.free()

        offset_x = -(nx - 1) * pitch / 2.0
        offset_y = -(ny - 1) * pitch / 2.0
        obj.location.x += offset_x
        obj.location.y += offset_y

        geometry.center_origin_to_bounds(context, obj)

        obj.name = f"Gridfinity_Lip_{nx}x{ny}"

        self.report({'INFO'}, f"Stacking Lip Array ({nx}x{ny}) created.")
        return {'FINISHED'}


class GRIDFINITY_OT_create_drawer_fitted_grid(bpy.types.Operator):
    """Generates a grid and cuts it exactly to the drawer dimensions on the far sides"""
    bl_idname = "gridfinity.create_drawer_fitted_grid"
    bl_label = "Create Drawer Fitted Grid"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        drawer_x = context.scene.gridfinity_drawer_x * 0.001
        drawer_y = context.scene.gridfinity_drawer_y * 0.001
        pitch = 0.042

        # Calculate the maximum required grid units by rounding up
        nx = math.ceil(drawer_x / pitch)
        ny = math.ceil(drawer_y / pitch)

        # Store the original grid values
        orig_nx = context.scene.gridfinity_x
        orig_ny = context.scene.gridfinity_y

        # Override the values for the array operator
        context.scene.gridfinity_x = nx
        context.scene.gridfinity_y = ny

        # Call the existing array operator
        bpy.ops.gridfinity.create_lip_array()

        # Reference the newly created grid object
        grid_obj = context.active_object

        # Restore original values
        context.scene.gridfinity_x = orig_nx
        context.scene.gridfinity_y = orig_ny

        # Move grid so the bottom left corner is exactly at X=0, Y=0
        grid_min_x = -(nx - 1) * pitch / 2.0 - 0.021
        grid_min_y = -(ny - 1) * pitch / 2.0 - 0.021
        grid_obj.location.x -= grid_min_x
        grid_obj.location.y -= grid_min_y

        # Create cutter object
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        cutter = context.active_object
        cutter.name = "Gridfinity_Drawer_Cutter"
        cutter.display_type = 'WIRE'

        # Scale cutter to drawer dimensions and ensure enough height for the cut
        bm_cutter = bmesh.new()
        bm_cutter.from_mesh(cutter.data)
        bmesh.ops.scale(bm_cutter, vec=(drawer_x, drawer_y, 0.1), verts=bm_cutter.verts)
        bm_cutter.to_mesh(cutter.data)
        bm_cutter.free()

        # Move cutter so its bottom left corner is also at X=0, Y=0
        cutter.location.x = drawer_x / 2.0
        cutter.location.y = drawer_y / 2.0

        # Apply boolean modifier to the grid for intersection
        bool_mod = grid_obj.modifiers.new(name="Drawer_Cut", type='BOOLEAN')
        bool_mod.operation = 'INTERSECT'
        bool_mod.object = cutter
        bool_mod.solver = 'EXACT'

        # Apply the modifier
        context.view_layer.objects.active = grid_obj
        bpy.ops.object.modifier_apply(modifier=bool_mod.name)

        # Remove the cutter
        bpy.data.objects.remove(cutter, do_unlink=True)

        # Center the cut grid back to the origin
        grid_obj.location.x -= drawer_x / 2.0
        grid_obj.location.y -= drawer_y / 2.0

        geometry.center_origin_to_bounds(context, grid_obj)



        self.report({'INFO'}, f"Fitted Grid created and cut to {drawer_x * 1000} x {drawer_y * 1000} mm.")
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
