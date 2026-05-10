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

    def finalize_object(self, obj, name):
        obj.name = name
        geometry.center_origin_to_bounds(obj)
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
        return self.finalize_object(obj, final_name)


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
        return self.finalize_object(obj, final_name)


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
        return self.finalize_object(obj, final_name)


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
        return self.finalize_object(bin_obj, final_name)


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
        return self.finalize_object(bin_obj, final_name)


class GRIDFINITY_OT_create_stacking_lip_array(GridfinityBaseOperator):
    """Generate grid array using Marching Squares neighbor logic"""
    bl_idname = "gridfinity.create_stacking_lip_array"
    bl_label = "Create Stacking Lip Array"

    def execute(self, context):
        params = self.get_base_params(context)
        nx = params['nx']
        ny = params['ny']

        final_obj = geometry.generate_lip_array(context, nx, ny)

        if not final_obj:
            self.report({'ERROR'}, "Failed to generate lip array geometry")
            return {'CANCELLED'}

        self.report({'INFO'}, f"Merged array {nx}x{ny} generated successfully")

        final_name = f"Gridfinity_Lip_Array_{nx}x{ny}"
        return self.finalize_object(final_obj, final_name)


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

        grid_obj = geometry.generate_lip_array(context, nx, ny)

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
        return self.finalize_object(grid_obj, final_name)


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
