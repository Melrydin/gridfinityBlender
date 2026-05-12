import bpy
import bmesh
import mathutils
from . import geometry


def create_object_from_bmesh(name, bm, collection):
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def apply_modifiers_via_depsgraph(obj, depsgraph):
    eval_obj = obj.evaluated_get(depsgraph)
    new_mesh = bpy.data.meshes.new_from_object(eval_obj)

    old_mesh = obj.data
    obj.data = new_mesh
    obj.modifiers.clear()

    bpy.data.meshes.remove(old_mesh)


def setup_array_modifiers(obj, nx, ny):
    if nx > 1:
        mod_x = obj.modifiers.new(name="Array_X", type='ARRAY')
        mod_x.count = nx
        mod_x.use_relative_offset = False
        mod_x.use_constant_offset = True
        mod_x.constant_offset_displace = (geometry.GRIDFINITY_PITCH, 0.0, 0.0)
        mod_x.use_merge_vertices = True
        mod_x.merge_threshold = 0.0001

    if ny > 1:
        mod_y = obj.modifiers.new(name="Array_Y", type='ARRAY')
        mod_y.count = ny
        mod_y.use_relative_offset = False
        mod_y.use_constant_offset = True
        mod_y.constant_offset_displace = (0.0, geometry.GRIDFINITY_PITCH, 0.0)
        mod_y.use_merge_vertices = True
        mod_y.merge_threshold = 0.0001


def center_origin_to_bounds(obj):
    mesh = obj.data
    if not mesh.vertices:
        return

    min_x = min(v.co.x for v in mesh.vertices)
    max_x = max(v.co.x for v in mesh.vertices)
    min_y = min(v.co.y for v in mesh.vertices)
    max_y = max(v.co.y for v in mesh.vertices)
    min_z = min(v.co.z for v in mesh.vertices)

    center_x = (min_x + max_x) / 2.0
    center_y = (min_y + max_y) / 2.0
    center = mathutils.Vector((center_x, center_y, min_z))

    for v in mesh.vertices:
        v.co -= center

    mesh.update()
    obj.location = (0.0, 0.0, min_z)


class GridfinityBaseOperator(bpy.types.Operator):
    bl_options = {'REGISTER', 'UNDO'}

    def get_base_params(self, context):
        props = context.scene.gridfinity
        return {
            'nx': props.x,
            'ny': props.y,
            'height_mm': props.bin_height,
            'thickness_mm': props.bin_wall_thickness,
            'use_magnets': props.use_magnets,
            'use_infill': props.use_infill,
            'depsgraph': context.evaluated_depsgraph_get(),
            'bin_add_profile': props.bin_add_profile
        }

    def finalize_object(self, context, obj, name):
        if obj.name not in context.collection.objects:
            context.collection.objects.link(obj)
        obj.name = name
        center_origin_to_bounds(obj)
        return {'FINISHED'}

    def generate_processed_baseplate(self, context, params):
        collection = context.collection
        depsgraph = params['depsgraph']

        bm_base = geometry.create_baseplate_unit_mesh()
        obj = create_object_from_bmesh("Gridfinity_Baseplate", bm_base, collection)

        if params['use_magnets']:
            bm_cutter = geometry.create_magnet_cutter()
            cutter_obj = create_object_from_bmesh("Magnet_Cutter", bm_cutter, collection)

            bool_mod = obj.modifiers.new(name="Gridfinity_Holes", type='BOOLEAN')
            bool_mod.operation = 'DIFFERENCE'
            bool_mod.object = cutter_obj
            bool_mod.solver = 'EXACT'

            context.view_layer.update()
            depsgraph = context.evaluated_depsgraph_get()

            apply_modifiers_via_depsgraph(obj, depsgraph)

            bpy.data.objects.remove(cutter_obj, do_unlink=True)

        setup_array_modifiers(obj, params['nx'], params['ny'])

        if params['nx'] > 1 or params['ny'] > 1:
            context.view_layer.update()
            depsgraph = context.evaluated_depsgraph_get()

            apply_modifiers_via_depsgraph(obj, depsgraph)

        return obj


class GRIDFINITY_OT_create_lid(GridfinityBaseOperator):
    """Create a flush fitting lid for standard bins"""
    bl_idname = "gridfinity.create_lid"
    bl_label = "Create Gridfinity Lid"

    def execute(self, context):
        params = self.get_base_params(context)
        props = context.scene.gridfinity

        bm_lid = geometry.create_lid_mesh(
            params['nx'],
            params['ny'],
            props.lid_thickness,
            props.bin_wall_thickness,
            props.lid_tolerance

        )

        if props.lid_add_profile:
            bm_lid = geometry.apply_stacking_profile_to_lid(bm_lid)

        obj = create_object_from_bmesh("Gridfinity_Lid", bm_lid, context.collection)

        self.report({'INFO'}, "Gridfinity lid created.")

        final_name = f"Gridfinity_Lid_{params['nx']}x{params['ny']}_T{int(props.lid_thickness)}"
        return self.finalize_object(context, obj, final_name)


class GRIDFINITY_OT_create_bin(GridfinityBaseOperator):
    """Create a hollow Gridfinity bin on top of the baseplate with inner bottom bevel"""
    bl_idname = "gridfinity.create_bin"
    bl_label = "Create Gridfinity Bin"

    def execute(self, context):
        params = self.get_base_params(context)

        bm_bin = geometry.create_bin_mesh(
            params['nx'],
            params['ny'],
            params['height_mm'],
            params['thickness_mm'],
            params['bin_add_profile']
        )

        obj = create_object_from_bmesh("Gridfinity_Bin", bm_bin, context.collection)

        self.report({'INFO'}, "Gridfinity bin with inner bottom bevel created.")

        final_name = f"Gridfinity_Box_{params['nx']}x{params['ny']}_H{int(params['height_mm'])}"
        return self.finalize_object(context, obj, final_name)


class GRIDFINITY_OT_create_solid_bin(GridfinityBaseOperator):
    """Create a solid Gridfinity bin with a 2mm top rim and inner bottom bevel"""
    bl_idname = "gridfinity.create_solid_bin"
    bl_label = "Create Solid Bin"

    def execute(self, context):
        params = self.get_base_params(context)

        bm_bin = geometry.create_solid_bin_mesh(
            params['nx'],
            params['ny'],
            params['height_mm'],
            params['thickness_mm'],
            params['bin_add_profile']
        )

        obj = create_object_from_bmesh("Gridfinity_Solid_Bin", bm_bin, context.collection)

        self.report({'INFO'}, "Solid Gridfinity bin with 2mm rim and inner bevel created.")

        final_name = f"Gridfinity_Complete_SolidBox_{params['nx']}x{params['ny']}_H{int(params['height_mm'])}"
        return self.finalize_object(context, obj, final_name)


class GRIDFINITY_OT_create_baseplate(GridfinityBaseOperator):
    """Create a Gridfinity baseplate unit restricted to 4.75mm height"""
    bl_idname = "gridfinity.create_baseplate"
    bl_label = "Create Gridfinity Baseplate"

    def execute(self, context):
        params = self.get_base_params(context)

        obj = self.generate_processed_baseplate(context, params)

        self.report({'INFO'}, "Gridfinity baseplate created with exactly 4.75mm height.")

        final_name = f"Gridfinity_Baseplate_{params['nx']}x{params['ny']}"
        return self.finalize_object(context, obj, final_name)


class GRIDFINITY_OT_create_baseplate_with_bin(GridfinityBaseOperator):
    """Create a Gridfinity baseplate with a hollow bin on top"""
    bl_idname = "gridfinity.create_baseplate_with_bin"
    bl_label = "Baseplate + Hollow Bin"

    def execute(self, context):
        params = self.get_base_params(context)

        baseplate_obj = self.generate_processed_baseplate(context, params)
        self.finalize_object(context, baseplate_obj, f"Gridfinity_Baseplate_{params['nx']}x{params['ny']}")

        bm_bin = geometry.create_bin_mesh(
            params['nx'],
            params['ny'],
            params['height_mm'],
            params['thickness_mm'],
            params['bin_add_profile']
        )

        bin_obj = create_object_from_bmesh("Gridfinity_Bin", bm_bin, context.collection)

        self.report({'INFO'}, "Gridfinity baseplate with hollow bin created.")

        final_name = f"Gridfinity_Complete_Box_{params['nx']}x{params['ny']}_H{int(params['height_mm'])}"
        return self.finalize_object(context, bin_obj, final_name)


class GRIDFINITY_OT_create_baseplate_with_solid_bin(GridfinityBaseOperator):
    """Create a Gridfinity baseplate with a solid bin on top"""
    bl_idname = "gridfinity.create_baseplate_with_solid_bin"
    bl_label = "Baseplate + Solid Bin"

    def execute(self, context):
        params = self.get_base_params(context)

        baseplate_obj = self.generate_processed_baseplate(context, params)
        self.finalize_object(context, baseplate_obj, f"Gridfinity_Baseplate_{params['nx']}x{params['ny']}")

        bm_bin = geometry.create_solid_bin_mesh(
            params['nx'],
            params['ny'],
            params['height_mm'],
            params['thickness_mm'],
            params['bin_add_profile']
        )

        bin_obj = create_object_from_bmesh("Gridfinity_Solid_Bin", bm_bin, context.collection)

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

        try:
            verts, faces = geometry.generate_lip_array(nx, ny, params['use_magnets'], params['use_infill'])
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        if not verts:
            self.report({'ERROR'}, "Failed to generate lip array geometry")
            return {'CANCELLED'}

        mesh = bpy.data.meshes.new(f"Gridfinity_Lip_Array_{nx}x{ny}_Mesh")
        mesh.from_pydata(verts, [], faces)
        mesh.update()

        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
        bm.to_mesh(mesh)
        bm.free()

        final_obj = bpy.data.objects.new(f"Gridfinity_Lip_Array_{nx}x{ny}", mesh)
        context.collection.objects.link(final_obj)

        self.report({'INFO'}, f"Merged array {nx}x{ny} generated successfully")

        final_name = f"Gridfinity_Lip_Array_{nx}x{ny}"
        return self.finalize_object(context, final_obj, final_name)


class GRIDFINITY_OT_create_drawer_fitted_grid(GridfinityBaseOperator):
    """Creates a grid and cuts it to the exact drawer dimensions directly via depsgraph"""
    bl_idname = "gridfinity.create_drawer_fitted_grid"
    bl_label = "Create Fitted Drawer Grid"

    def execute(self, context):
        props = context.scene.gridfinity
        drawer_x = props.drawer_x
        drawer_y = props.drawer_y

        params = self.get_base_params(context)

        pitch_mm = geometry.GRIDFINITY_PITCH * 1000.0

        nx = int((drawer_x / pitch_mm) + 1)
        ny = int((drawer_y / pitch_mm) + 1)

        try:
            verts, faces = geometry.generate_lip_array(nx, ny, params['use_magnets'], params['use_infill'])
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        if not verts:
            self.report({'ERROR'}, "Array generation failed")
            return {'CANCELLED'}

        mesh = bpy.data.meshes.new(f"Gridfinity_Drawer_Grid_Mesh")
        mesh.from_pydata(verts, [], faces)
        mesh.update()

        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
        bm.to_mesh(mesh)
        bm.free()

        grid_obj = bpy.data.objects.new("Gridfinity_Drawer_Grid", mesh)
        context.collection.objects.link(grid_obj)

        cutter_mesh = bpy.data.meshes.new("Drawer_Cutter_Mesh")
        cutter = bpy.data.objects.new("Drawer_Cutter_Temp", cutter_mesh)
        context.collection.objects.link(cutter)

        bm_cutter = bmesh.new()
        bmesh.ops.create_cube(bm_cutter, size=1.0)

        size_x = (drawer_x * 0.001) + 1.0
        size_y = (drawer_y * 0.001) + 1.0
        size_z = 1.0

        bmesh.ops.scale(bm_cutter, vec=(size_x, size_y, size_z), verts=bm_cutter.verts)

        loc_x = ((drawer_x * 0.001) - 1.0) / 2.0
        loc_y = ((drawer_y * 0.001) - 1.0) / 2.0
        bmesh.ops.translate(bm_cutter, vec=(loc_x, loc_y, 0.0), verts=bm_cutter.verts)

        bm_cutter.to_mesh(cutter_mesh)
        bm_cutter.free()

        bool_mod = grid_obj.modifiers.new(name="Drawer_Cut", type='BOOLEAN')
        bool_mod.operation = 'INTERSECT'
        bool_mod.object = cutter
        bool_mod.solver = 'FAST'

        context.view_layer.update()
        apply_modifiers_via_depsgraph(grid_obj, params['depsgraph'])

        bpy.data.objects.remove(cutter, do_unlink=True)
        bpy.data.meshes.remove(cutter_mesh)

        self.report({'INFO'}, f"Grid fitted to {int(drawer_x)}mm x {int(drawer_y)}mm")

        final_name = f"Gridfinity_Drawer_Grid_{int(drawer_x)}x{int(drawer_y)}"
        return self.finalize_object(context, grid_obj, final_name)


def register():
    bpy.utils.register_class(GRIDFINITY_OT_create_baseplate)
    bpy.utils.register_class(GRIDFINITY_OT_create_bin)
    bpy.utils.register_class(GRIDFINITY_OT_create_solid_bin)
    bpy.utils.register_class(GRIDFINITY_OT_create_baseplate_with_bin)
    bpy.utils.register_class(GRIDFINITY_OT_create_baseplate_with_solid_bin)
    bpy.utils.register_class(GRIDFINITY_OT_create_stacking_lip_array)
    bpy.utils.register_class(GRIDFINITY_OT_create_drawer_fitted_grid)
    bpy.utils.register_class(GRIDFINITY_OT_create_lid)


def unregister():
    bpy.utils.unregister_class(GRIDFINITY_OT_create_baseplate)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_bin)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_solid_bin)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_baseplate_with_bin)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_baseplate_with_solid_bin)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_stacking_lip_array)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_drawer_fitted_grid)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_lid)
