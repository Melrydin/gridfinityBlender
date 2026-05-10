import bpy
import bmesh
import os

UNIT_SIZE = 0.0415
SPACING = 0.001
PITCH = UNIT_SIZE + SPACING
BASE_HEIGHT = 0.00475


def create_baseplate_unit_mesh(context):
    """
    Create a single Gridfinity baseplate unit restricted to 4.75mm height.
    Origin is at (0, 0, 0) - center of geometry in X/Y, bottom at Z=0.

    Args:
        context: Blender context

    Returns:
        bpy.types.Object: The created baseplate unit object
    """
    mesh = bpy.data.meshes.new("Gridfinity_Baseplate_Mesh")
    obj = bpy.data.objects.new("Gridfinity_Baseplate", mesh)
    context.collection.objects.link(obj)
    context.view_layer.objects.active = obj
    obj.select_set(True)

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)

    vertical_edges = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 0.5]

    bmesh.ops.scale(bm, vec=(UNIT_SIZE, UNIT_SIZE, 0.00001), verts=bm.verts)
    bmesh.ops.translate(bm, vec=(0.0, 0.0, 0.0), verts=bm.verts)

    bmesh.ops.bevel(
        bm,
        geom=vertical_edges,
        offset=0.0075,
        segments=16,
        profile=0.5,
        affect='EDGES'
    )

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    bottom_face = min(bm.faces, key=lambda f: f.calc_center_median().z)

    if bottom_face:
        bmesh.ops.inset_region(bm, faces=[bottom_face], thickness=0.00215)
        for vert in bottom_face.verts:
            vert.co.z -= 0.00215

        bmesh.ops.inset_region(bm, faces=[bottom_face], thickness=0.00001)
        for vert in bottom_face.verts:
            vert.co.z -= 0.0018

        bmesh.ops.inset_region(bm, faces=[bottom_face], thickness=0.0008)
        for vert in bottom_face.verts:
            vert.co.z -= 0.0008

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.00005)

    min_z = min(v.co.z for v in bm.verts)
    bmesh.ops.translate(bm, vec=(0.0, 0.0, -min_z), verts=bm.verts)

    # Center X and Y
    center_x = sum(v.co.x for v in bm.verts) / len(bm.verts)
    center_y = sum(v.co.y for v in bm.verts) / len(bm.verts)
    bmesh.ops.translate(bm, vec=(-center_x, -center_y, 0.0), verts=bm.verts)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    # Magnet Holes
    if getattr(context.scene, "gridfinity_use_magnets", False):
        cutter_mesh = bpy.data.meshes.new("Magnet_Cutter_Mesh")
        cutter_obj = bpy.data.objects.new("Magnet_Cutter", cutter_mesh)
        context.collection.objects.link(cutter_obj)

        c_bm = bmesh.new()
        offsets = [(0.013, 0.013), (0.013, -0.013), (-0.013, 0.013), (-0.013, -0.013)]

        for ox, oy in offsets:
            # Magnet void: 6.5mm diameter, 2.4mm deep
            # Extending slightly below Z=0 to prevent Z-fighting (-1mm to 2.4mm)
            mag = bmesh.ops.create_cone(c_bm, cap_ends=True, cap_tris=False, segments=64, radius1=0.00325, radius2=0.00325, depth=0.0034)
            bmesh.ops.translate(c_bm, vec=(ox, oy, 0.0007), verts=mag['verts'])

        c_bm.to_mesh(cutter_mesh)
        c_bm.free()

        # Apply Boolean Difference
        context.view_layer.objects.active = obj
        bool_mod = obj.modifiers.new(name="Gridfinity_Holes", type='BOOLEAN')
        bool_mod.operation = 'DIFFERENCE'
        bool_mod.object = cutter_obj
        bool_mod.solver = 'EXACT'

        bpy.ops.object.modifier_apply(modifier="Gridfinity_Holes")
        bpy.data.objects.remove(cutter_obj, do_unlink=True)

    return obj


def create_bin_mesh(context, nx, ny, height_mm, thickness_mm):
    """
    Create a hollow Gridfinity bin on top of the baseplate with inner bottom bevel.
    Origin is at (0, 0, 0) - center of geometry in X/Y, bottom at Z=0.

    Args:
        context: Blender context
        nx: Number of units in X direction
        ny: Number of units in Y direction
        height_mm: Bin height in millimeters
        thickness_mm: Bin wall thickness in millimeters

    Returns:
        bpy.types.Object: The created bin object
    """

    width = UNIT_SIZE + (nx - 1) * PITCH
    depth = UNIT_SIZE + (ny - 1) * PITCH
    height = height_mm * 0.001
    thickness = thickness_mm * 0.001
    base_height = BASE_HEIGHT

    mesh = bpy.data.meshes.new("Gridfinity_Bin_Mesh")
    obj = bpy.data.objects.new("Gridfinity_Bin", mesh)
    context.collection.objects.link(obj)
    context.view_layer.objects.active = obj
    obj.select_set(True)

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)

    bmesh.ops.scale(bm, vec=(width, depth, height), verts=bm.verts)

    center_z = base_height + (height / 2.0)
    bmesh.ops.translate(bm, vec=(0.0, 0.0, center_z), verts=bm.verts)

    vertical_edges = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 0.001]

    bmesh.ops.bevel(
        bm,
        geom=vertical_edges,
        offset=0.0075,
        segments=16,
        profile=0.5,
        affect='EDGES'
    )

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    top_face = max(bm.faces, key=lambda f: f.calc_center_median().z)
    bmesh.ops.inset_region(bm, faces=[top_face], thickness=thickness)

    geom_to_extrude = [top_face] + list(top_face.edges)
    extrude_result = bmesh.ops.extrude_face_region(bm, geom=geom_to_extrude)
    extruded_verts = [elem for elem in extrude_result['geom'] if isinstance(elem, bmesh.types.BMVert)]

    bmesh.ops.translate(bm, vec=(0.0, 0.0, -(height - thickness)), verts=extruded_verts)

    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()

    inner_bottom_edges = [e for e in bm.edges if e.verts[0] in extruded_verts and e.verts[1] in extruded_verts]

    bmesh.ops.bevel(
        bm,
        geom=inner_bottom_edges,
        offset=0.001,
        segments=8,
        profile=0.5,
        affect='EDGES'
    )

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    return obj


def create_solid_bin_mesh(context, nx, ny, height_mm, thickness_mm):
    """
    Create a solid Gridfinity bin with a 2mm top rim and inner bottom bevel.
    Origin is at (0, 0, 0) - center of geometry in X/Y, bottom at Z=0.

    Args:
        context: Blender context
        nx: Number of units in X direction
        ny: Number of units in Y direction
        height_mm: Bin height in millimeters
        thickness_mm: Bin wall thickness in millimeters

    Returns:
        bpy.types.Object: The created solid bin object
    """

    width = UNIT_SIZE + (nx - 1) * PITCH
    depth = UNIT_SIZE + (ny - 1) * PITCH
    height = height_mm * 0.001
    thickness = thickness_mm * 0.001
    base_height = BASE_HEIGHT
    rim_depth = 0.002

    mesh = bpy.data.meshes.new("Gridfinity_Solid_Bin_Mesh")
    obj = bpy.data.objects.new("Gridfinity_Solid_Bin", mesh)
    context.collection.objects.link(obj)
    context.view_layer.objects.active = obj
    obj.select_set(True)

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)

    bmesh.ops.scale(bm, vec=(width, depth, height), verts=bm.verts)

    center_z = base_height + (height / 2.0)
    bmesh.ops.translate(bm, vec=(0.0, 0.0, center_z), verts=bm.verts)

    vertical_edges = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 0.001]

    bmesh.ops.bevel(
        bm,
        geom=vertical_edges,
        offset=0.0075,
        segments=16,
        profile=0.5,
        affect='EDGES'
    )

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    top_face = max(bm.faces, key=lambda f: f.calc_center_median().z)
    bmesh.ops.inset_region(bm, faces=[top_face], thickness=thickness)

    geom_to_extrude = [top_face] + list(top_face.edges)
    extrude_result = bmesh.ops.extrude_face_region(bm, geom=geom_to_extrude)
    extruded_verts = [elem for elem in extrude_result['geom'] if isinstance(elem, bmesh.types.BMVert)]

    bmesh.ops.translate(bm, vec=(0.0, 0.0, -rim_depth), verts=extruded_verts)

    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()

    inner_bottom_edges = [e for e in bm.edges if e.verts[0] in extruded_verts and e.verts[1] in extruded_verts]

    bmesh.ops.bevel(
        bm,
        geom=inner_bottom_edges,
        offset=0.001,
        segments=8,
        profile=0.5,
        affect='EDGES'
    )

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    return obj


def apply_grid_array(obj, nx, ny):

    if nx > 1:
        mod_x = obj.modifiers.new(name="Array_X", type='ARRAY')
        mod_x.count = nx
        mod_x.use_relative_offset = False
        mod_x.use_constant_offset = True
        mod_x.constant_offset_displace = (PITCH, 0.0, 0.0)
        mod_x.use_merge_vertices = True
        mod_x.merge_threshold = 0.0001
        bpy.ops.object.modifier_apply(modifier="Array_X")

    if ny > 1:
        mod_y = obj.modifiers.new(name="Array_Y", type='ARRAY')
        mod_y.count = ny
        mod_y.use_relative_offset = False
        mod_y.use_constant_offset = True
        mod_y.constant_offset_displace = (0.0, PITCH, 0.0)
        mod_y.use_merge_vertices = True
        mod_y.merge_threshold = 0.0001
        bpy.ops.object.modifier_apply(modifier="Array_Y")

    offset_x = (nx - 1) * PITCH / 2.0
    offset_y = (ny - 1) * PITCH / 2.0
    obj.location.x -= offset_x
    obj.location.y -= offset_y


def center_origin_to_bounds(context, obj):
    """
    Sets the origin of the given object to the center of its bounding box.

    Args:
        context: Blender context
        obj: The object to center
    """
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')


def load_reference_object(context, filename):
    addon_dir = os.path.dirname(__file__)
    filepath = os.path.join(addon_dir, "geometry", filename)

    if not os.path.exists(filepath):
        print(f"Error: File missing: {filename}")
        return None

    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.wm.obj_import(filepath=filepath)

    if not context.selected_objects:
        return None

    obj = context.selected_objects[0]
    context.view_layer.objects.active = obj

    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    return obj
