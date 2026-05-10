import bpy
from . import geometry
import math
import bmesh
import mathutils


class GridfinityBaseOperator(bpy.types.Operator):
    bl_options = {'REGISTER', 'UNDO'}

    def get_base_params(self, context):
        return {
            'nx': context.scene.gridfinity_x,
            'ny': context.scene.gridfinity_y,
            'height_mm': context.scene.gridfinity_bin_height,
            'thickness_mm': context.scene.gridfinity_bin_wall_thickness
        }

    def finalize_object(self, context, obj, name):
        obj.name = name
        geometry.center_origin_to_bounds(context, obj)
        return {'FINISHED'}


class GRIDFINITY_OT_create_bin(GridfinityBaseOperator):
    """Create a hollow Gridfinity bin on top of the baseplate with inner bottom bevel"""
    bl_idname = "gridfinity.create_bin"
    bl_label = "Create Gridfinity Bin"

    def execute(self, context):
        params = self.get_base_params(context)

        obj = geometry.create_bin_mesh(
            context,
            params['nx'],
            params['ny'],
            params['height_mm'],
            params['thickness_mm']
        )

        self.report({'INFO'}, "Gridfinity bin with inner bottom bevel created.")

        final_name = f"Gridfinity_Box_{params['nx']}x{params['ny']}_H{int(params['height_mm'])}"
        return self.finalize_object(context, obj, final_name)


class GRIDFINITY_OT_create_solid_bin(GridfinityBaseOperator):
    """Create a solid Gridfinity bin with a 2mm top rim and inner bottom bevel"""
    bl_idname = "gridfinity.create_solid_bin"
    bl_label = "Create Solid Bin"

    def execute(self, context):
        params = self.get_base_params(context)

        obj = geometry.create_solid_bin_mesh(
            context,
            params['nx'],
            params['ny'],
            params['height_mm'],
            params['thickness_mm']
        )

        self.report({'INFO'}, "Solid Gridfinity bin with 2mm rim and inner bevel created.")

        final_name = f"Gridfinity_Complete_SolidBox_{params['nx']}x{params['ny']}_H{int(params['height_mm'])}"
        return self.finalize_object(context, obj, final_name)


class GRIDFINITY_OT_create_baseplate(GridfinityBaseOperator):
    """Create a Gridfinity baseplate unit restricted to 4.75mm height"""
    bl_idname = "gridfinity.create_baseplate"
    bl_label = "Create Gridfinity Baseplate"

    def execute(self, context):
        params = self.get_base_params(context)

        obj = geometry.create_baseplate_unit_mesh(context)
        geometry.apply_grid_array(obj, params['nx'], params['ny'])

        self.report({'INFO'}, "Gridfinity baseplate created with exactly 4.75mm height.")

        final_name = f"Gridfinity_Baseplate_{params['nx']}x{params['ny']}"
        return self.finalize_object(context, obj, final_name)


class GRIDFINITY_OT_create_baseplate_with_bin(GridfinityBaseOperator):
    """Create a Gridfinity baseplate with a hollow bin on top"""
    bl_idname = "gridfinity.create_baseplate_with_bin"
    bl_label = "Baseplate + Hollow Bin"

    def execute(self, context):
        params = self.get_base_params(context)

        baseplate_obj = geometry.create_baseplate_unit_mesh(context)
        geometry.apply_grid_array(baseplate_obj, params['nx'], params['ny'])
        baseplate_obj.name = f"Gridfinity_Baseplate_{params['nx']}x{params['ny']}"
        geometry.center_origin_to_bounds(context, baseplate_obj)

        bin_obj = geometry.create_bin_mesh(
            context,
            params['nx'],
            params['ny'],
            params['height_mm'],
            params['thickness_mm']
        )

        self.report({'INFO'}, "Gridfinity baseplate with hollow bin created.")

        final_name = f"Gridfinity_Complete_Box_{params['nx']}x{params['ny']}_H{int(params['height_mm'])}"
        return self.finalize_object(context, bin_obj, final_name)


class GRIDFINITY_OT_create_baseplate_with_solid_bin(GridfinityBaseOperator):
    """Create a Gridfinity baseplate with a solid bin on top"""
    bl_idname = "gridfinity.create_baseplate_with_solid_bin"
    bl_label = "Baseplate + Solid Bin"

    def execute(self, context):
        params = self.get_base_params(context)

        baseplate_obj = geometry.create_baseplate_unit_mesh(context)
        geometry.apply_grid_array(baseplate_obj, params['nx'], params['ny'])
        baseplate_obj.name = f"Gridfinity_Baseplate_{params['nx']}x{params['ny']}"
        geometry.center_origin_to_bounds(context, baseplate_obj)

        bin_obj = geometry.create_solid_bin_mesh(
            context,
            params['nx'],
            params['ny'],
            params['height_mm'],
            params['thickness_mm']
        )

        self.report({'INFO'}, "Gridfinity baseplate with solid bin created.")

        final_name = f"Gridfinity_Complete_SolidBox_{params['nx']}x{params['ny']}_H{int(params['height_mm'])}"
        return self.finalize_object(context, bin_obj, final_name)


class GRIDFINITY_OT_create_stacking_lip_array(GridfinityBaseOperator):
    """Generate grid array using Marching Squares neighbor logic"""
    bl_idname = "gridfinity.create_stacking_lip_array"
    bl_label = "Create Stacking Lip Array"

    def execute(self, context):
        params = self.get_base_params(context)
        nx = params['nx']
        ny = params['ny']

        final_obj = _generate_lip_array(context, nx, ny)

        if not final_obj:
            self.report({'ERROR'}, "Failed to generate lip array geometry")
            return {'CANCELLED'}

        self.report({'INFO'}, f"Merged array {nx}x{ny} generated successfully")

        final_name = f"Gridfinity_Lip_Array_{nx}x{ny}"
        return self.finalize_object(context, final_obj, final_name)


class GRIDFINITY_OT_create_drawer_fitted_grid(GridfinityBaseOperator):
    """Creates a grid and cuts it to the exact drawer dimensions directly via depsgraph"""
    bl_idname = "gridfinity.create_drawer_fitted_grid"
    bl_label = "Create Fitted Drawer Grid"

    def execute(self, context):
        drawer_x = context.scene.gridfinity_drawer_x
        drawer_y = context.scene.gridfinity_drawer_y

        pitch_mm = geometry.GRIDFINITY_PITCH * 1000.0

        nx = int((drawer_x / pitch_mm) + 1)
        ny = int((drawer_y / pitch_mm) + 1)

        grid_obj = _generate_lip_array(context, nx, ny)

        if not grid_obj:
            self.report({'ERROR'}, "Array generation failed")
            return {'CANCELLED'}

        mesh = bpy.data.meshes.new("Drawer_Cutter_Mesh")
        cutter = bpy.data.objects.new("Drawer_Cutter_Temp", mesh)
        context.collection.objects.link(cutter)

        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)

        size_x = (drawer_x * 0.001) + 1.0
        size_y = (drawer_y * 0.001) + 1.0
        size_z = 1.0

        bmesh.ops.scale(bm, vec=(size_x, size_y, size_z), verts=bm.verts)

        loc_x = ((drawer_x * 0.001) - 1.0) / 2.0
        loc_y = ((drawer_y * 0.001) - 1.0) / 2.0
        bmesh.ops.translate(bm, vec=(loc_x, loc_y, 0.0), verts=bm.verts)

        bm.to_mesh(mesh)
        bm.free()

        bool_mod = grid_obj.modifiers.new(name="Drawer_Cut", type='BOOLEAN')
        bool_mod.operation = 'INTERSECT'
        bool_mod.object = cutter
        bool_mod.solver = 'FAST'

        context.view_layer.update()
        geometry.apply_modifiers_via_depsgraph(context, grid_obj)

        bpy.data.objects.remove(cutter, do_unlink=True)
        bpy.data.meshes.remove(mesh)

        self.report({'INFO'}, f"Grid fitted to {int(drawer_x)}mm x {int(drawer_y)}mm")

        final_name = f"Gridfinity_Drawer_Grid_{int(drawer_x)}x{int(drawer_y)}"
        return self.finalize_object(context, grid_obj, final_name)


def _generate_lip_array(context, nx, ny):
    """
    Generates the merged lip array purely via data structures and matrix math,
    bypassing all bpy.ops and selection states.
    """
    if context.scene.gridfinity_use_magnets:
        if context.scene.gridfinity_use_infill:
            obj_l = geometry.load_reference_object(context, "baseplate_L_magnet.obj")
            obj_t = geometry.load_reference_object(context, "baseplate_T_magnet_filled.obj")
            obj_x = geometry.load_reference_object(context, "baseplate_X_magnet_filled.obj")
        else:
            obj_l = geometry.load_reference_object(context, "baseplate_L_magnet.obj")
            obj_t = geometry.load_reference_object(context, "baseplate_T_magnet.obj")
            obj_x = geometry.load_reference_object(context, "baseplate_X_magnet.obj")
    else:
        if context.scene.gridfinity_use_infill:
            obj_l = geometry.load_reference_object(context, "baseplate_L.obj")
            obj_t = geometry.load_reference_object(context, "baseplate_T_filled.obj")
            obj_x = geometry.load_reference_object(context, "baseplate_X_filled.obj")
        else:
            obj_l = geometry.load_reference_object(context, "baseplate_L.obj")
            obj_t = geometry.load_reference_object(context, "baseplate_T.obj")
            obj_x = geometry.load_reference_object(context, "baseplate_X.obj")

    if not obj_l or not obj_t or not obj_x:
        return None

    grid = [[True for _ in range(ny)] for _ in range(nx)]

    def cell_exists(cx, cy):
        if 0 <= cx < nx and 0 <= cy < ny:
            return grid[cx][cy]
        return False

    state_lookup = {
        (True, False, False, False): (obj_l, math.radians(180)),
        (False, True, False, False): (obj_l, math.radians(-90)),
        (False, False, True, False): (obj_l, math.radians(0)),
        (False, False, False, True): (obj_l, math.radians(90)),
        (True, True, False, False):  (obj_t, math.radians(180)),
        (False, True, True, False):  (obj_t, math.radians(-90)),
        (False, False, True, True):  (obj_t, math.radians(0)),
        (True, False, False, True):  (obj_t, math.radians(90)),
        (True, True, True, True):    (obj_x, math.radians(0))
    }

    all_verts = []
    all_faces = []
    vert_offset = 0

    for x in range(nx + 1):
        for y in range(ny + 1):
            tr = cell_exists(x, y)
            tl = cell_exists(x - 1, y)
            bl = cell_exists(x - 1, y - 1)
            br = cell_exists(x, y - 1)

            state = (tr, tl, bl, br)

            if state not in state_lookup:
                continue

            source_obj, rotation_z = state_lookup[state]
            source_mesh = source_obj.data

            matrix = mathutils.Matrix.Translation((x * geometry.GRIDFINITY_PITCH, y * geometry.GRIDFINITY_PITCH, 0.0)) @ mathutils.Matrix.Rotation(rotation_z, 4, 'Z')

            for v in source_mesh.vertices:
                all_verts.append(matrix @ v.co)

            for p in source_mesh.polygons:
                all_faces.append([v + vert_offset for v in p.vertices])

            vert_offset += len(source_mesh.vertices)

    bpy.data.objects.remove(obj_l, do_unlink=True)
    bpy.data.objects.remove(obj_t, do_unlink=True)
    bpy.data.objects.remove(obj_x, do_unlink=True)

    if not all_verts:
        return None

    merged_mesh = bpy.data.meshes.new(f"Gridfinity_Lip_Array_{nx}x{ny}_Mesh")
    merged_mesh.from_pydata(all_verts, [], all_faces)
    merged_mesh.update()

    bm = bmesh.new()
    bm.from_mesh(merged_mesh)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    bm.to_mesh(merged_mesh)
    bm.free()

    final_obj = bpy.data.objects.new(f"Gridfinity_Lip_Array_{nx}x{ny}", merged_mesh)
    context.collection.objects.link(final_obj)

    return final_obj


def register():
    bpy.utils.register_class(GRIDFINITY_OT_create_baseplate)
    bpy.utils.register_class(GRIDFINITY_OT_create_bin)
    bpy.utils.register_class(GRIDFINITY_OT_create_solid_bin)
    bpy.utils.register_class(GRIDFINITY_OT_create_baseplate_with_bin)
    bpy.utils.register_class(GRIDFINITY_OT_create_baseplate_with_solid_bin)
    bpy.utils.register_class(GRIDFINITY_OT_create_stacking_lip_array)
    bpy.utils.register_class(GRIDFINITY_OT_create_drawer_fitted_grid)


def unregister():
    bpy.utils.unregister_class(GRIDFINITY_OT_create_baseplate)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_bin)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_solid_bin)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_baseplate_with_bin)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_baseplate_with_solid_bin)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_stacking_lip_array)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_drawer_fitted_grid)
