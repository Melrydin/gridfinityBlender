import bmesh
import os
import mathutils
import math
import bpy

GRIDFINITY_PITCH = 0.042
GRIDFINITY_CLEARANCE = 0.0005
GRIDFINITY_BASE_HEIGHT = 0.00475


def create_baseplate_unit_mesh():
    """
    Create a single Gridfinity baseplate unit bmesh restricted to 4.75mm height.
    """
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)

    vertical_edges = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 0.5]

    bmesh.ops.scale(bm, vec=(GRIDFINITY_PITCH, GRIDFINITY_PITCH, 0.00001), verts=bm.verts)
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

    center_x = sum(v.co.x for v in bm.verts) / len(bm.verts)
    center_y = sum(v.co.y for v in bm.verts) / len(bm.verts)
    bmesh.ops.translate(bm, vec=(-center_x, -center_y, 0.0), verts=bm.verts)

    return bm


def create_magnet_cutter():
    """
    Creates the cutter bmesh for the magnet holes.
    """
    c_bm = bmesh.new()
    offsets = [(0.013, 0.013), (0.013, -0.013), (-0.013, 0.013), (-0.013, -0.013)]

    for ox, oy in offsets:
        mag = bmesh.ops.create_cone(c_bm, cap_ends=True, cap_tris=False, segments=64, radius1=0.00325, radius2=0.00325, depth=0.0034)
        bmesh.ops.translate(c_bm, vec=(ox, oy, 0.0007), verts=mag['verts'])

    return c_bm


def create_bin_mesh(nx, ny, height_mm, thickness_mm, add_profile=False):
    """
    Create a hollow Gridfinity bin bmesh.
    """
    bm, height = _create_base_bin_geometry(nx, ny, height_mm)
    thickness = thickness_mm * 0.001
    extrude_depth = height - thickness

    _apply_top_inset_and_bevel(bm, thickness, extrude_depth, add_profile)
    return bm


def create_solid_bin_mesh(nx, ny, height_mm, thickness_mm, add_profile=False):
    """
    Create a solid Gridfinity bin bmesh.
    """
    bm, _ = _create_base_bin_geometry(nx, ny, height_mm)
    thickness = thickness_mm * 0.001
    rim_depth = 0.002
    if add_profile:
        rim_depth += 0.0044


    _apply_top_inset_and_bevel(bm, thickness, rim_depth, add_profile)
    return bm


def _create_base_bin_geometry(nx, ny, height_mm):
    width = (nx * GRIDFINITY_PITCH) - GRIDFINITY_CLEARANCE
    depth = (ny * GRIDFINITY_PITCH) - GRIDFINITY_CLEARANCE
    height = height_mm * 0.001

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)

    bmesh.ops.scale(bm, vec=(width, depth, height), verts=bm.verts)

    center_z = GRIDFINITY_BASE_HEIGHT + (height / 2.0)
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

    return bm, height


def _apply_top_inset_and_bevel(bm, thickness, extrude_depth, add_profile):
    top_face = max(bm.faces, key=lambda f: f.calc_center_median().z)

    if add_profile:
        top_face, profile_depth = _apply_bin_top_profile(bm, top_face)
        extrude_depth -= profile_depth
    else:
        bmesh.ops.inset_region(bm, faces=[top_face], thickness=thickness)

    geom_to_extrude = [top_face] + list(top_face.edges)
    extrude_result = bmesh.ops.extrude_face_region(bm, geom=geom_to_extrude)
    extruded_verts = [elem for elem in extrude_result['geom'] if isinstance(elem, bmesh.types.BMVert)]

    bmesh.ops.translate(bm, vec=(0.0, 0.0, -extrude_depth), verts=extruded_verts)

    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()

    inner_bottom_edges = [e for e in bm.edges if e.verts[0] in extruded_verts and e.verts[1] in extruded_verts]

    if inner_bottom_edges:
        bmesh.ops.bevel(
            bm,
            geom=inner_bottom_edges,
            offset=0.001,
            segments=8,
            profile=0.5,
            affect='EDGES'
        )

    if add_profile:
        all_top_facing = [f for f in bm.faces if f.normal.z > 0.9]

        if all_top_facing:
            target_face = max(all_top_facing, key=lambda f: f.calc_center_median().z)
            bmesh.ops.delete(bm, geom=[target_face], context='FACES_ONLY')

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

def _apply_bin_top_profile(bm, top_face):
    """
    Creates the stacking lip profile on the top face of the bin.
    Returns the inner face and the Z depth of the profile.
    """

    bmesh.ops.inset_region(bm, faces=[top_face], thickness=0.0019, depth=-0.0019)

    bmesh.ops.inset_region(bm, faces=[top_face], thickness=0.0, depth=-0.0018)

    bmesh.ops.inset_region(bm, faces=[top_face], thickness=0.0007, depth=-0.0007)

    extrude_drop = bmesh.ops.extrude_face_region(bm, geom=[top_face])
    drop_verts = [elem for elem in extrude_drop['geom'] if isinstance(elem, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0.0, 0.0, -0.00045), verts=drop_verts)

    profile_depth = 0.0044
    return top_face, profile_depth

def create_lid_mesh(nx, ny, thickness_mm, wall_thickness_mm, tolerance_mm):
    """
    Create a Gridfinity lid base and extrude the inner alignment plug.
    """
    bm = bmesh.new()

    width = (nx * GRIDFINITY_PITCH) - GRIDFINITY_CLEARANCE
    depth = (ny * GRIDFINITY_PITCH) - GRIDFINITY_CLEARANCE
    thickness = thickness_mm * 0.001
    plug_height = 0.003

    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(width, depth, thickness), verts=bm.verts)

    center_z = plug_height + (thickness / 2.0)
    bmesh.ops.translate(bm, vec=(0.0, 0.0, center_z), verts=bm.verts)

    vertical_edges = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 0.0001]

    bmesh.ops.bevel(
        bm,
        geom=vertical_edges,
        offset=0.0075,
        segments=16,
        profile=0.5,
        affect='EDGES'
    )

    bm.faces.ensure_lookup_table()
    bottom_face = min(bm.faces, key=lambda f: f.calc_center_median().z)

    inset_thickness = (wall_thickness_mm + (tolerance_mm / 2.0)) * 0.001
    bmesh.ops.inset_region(bm, faces=[bottom_face], thickness=inset_thickness)

    extrude_result = bmesh.ops.extrude_face_region(bm, geom=[bottom_face])
    extruded_verts = [elem for elem in extrude_result['geom'] if isinstance(elem, bmesh.types.BMVert)]

    bmesh.ops.translate(bm, vec=(0.0, 0.0, -plug_height), verts=extruded_verts)

    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    return bm

def apply_stacking_profile_to_lid(bm):
    """
    Extends the top face of the lid upwards and extrudes the
    Gridfinity negative profile cavity into it.
    """
    bm.faces.ensure_lookup_table()

    top_face = max(bm.faces, key=lambda f: f.calc_center_median().z)

    lip_total_height = 0.0044
    extrude_up = bmesh.ops.extrude_face_region(bm, geom=[top_face])
    top_verts = [elem for elem in extrude_up['geom'] if isinstance(elem, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0.0, 0.0, lip_total_height), verts=top_verts)

    current_top_face = None
    for elem in extrude_up['geom']:
        if isinstance(elem, bmesh.types.BMFace) and elem.normal.z > 0.9:
            current_top_face = elem
            break

    if not current_top_face:
        return bm

    bmesh.ops.inset_region(bm, faces=[current_top_face], thickness=0.0019, depth=-0.0019)

    bmesh.ops.inset_region(bm, faces=[current_top_face], thickness=0.0, depth=-0.0018)

    bmesh.ops.inset_region(bm, faces=[current_top_face], thickness=0.0007, depth=-0.0007)

    extrude_drop = bmesh.ops.extrude_face_region(bm, geom=[current_top_face])
    drop_verts = [elem for elem in extrude_drop['geom'] if isinstance(elem, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0.0, 0.0, -0.00045), verts=drop_verts)

    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    return bm

def generate_lip_array(nx, ny, use_magnets, use_infill, stackable_baseplate):
    """
    Generates the merged lip array purely via data structures and matrix math,
    returning raw vertex coordinates and face indices.
    """

    suffix_stack = "_stackable" if stackable_baseplate else ""
    suffix_mag = "_magnet" if use_magnets else ""
    suffix_fill = "_filled" if use_infill else ""

    obj_l = load_reference_object(f"Gridfinity_baseplate_L{suffix_mag}{suffix_stack}")
    obj_t = load_reference_object(f"Gridfinity_baseplate_T{suffix_mag}{suffix_fill}{suffix_stack}")
    obj_x = load_reference_object(f"Gridfinity_baseplate_X{suffix_mag}{suffix_fill}{suffix_stack}")

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

            matrix = mathutils.Matrix.Translation((x * GRIDFINITY_PITCH, y * GRIDFINITY_PITCH, 0.0)) @ mathutils.Matrix.Rotation(rotation_z, 4, 'Z')

            for v in source_mesh.vertices:
                all_verts.append(matrix @ v.co)

            for p in source_mesh.polygons:
                all_faces.append([v + vert_offset for v in p.vertices])

            vert_offset += len(source_mesh.vertices)

    mesh_l = obj_l.data
    mesh_t = obj_t.data
    mesh_x = obj_x.data

    bpy.data.objects.remove(obj_l, do_unlink=True)
    bpy.data.objects.remove(obj_t, do_unlink=True)
    bpy.data.objects.remove(obj_x, do_unlink=True)

    if mesh_l.users == 0:
        bpy.data.meshes.remove(mesh_l)
    if mesh_t.users == 0:
        bpy.data.meshes.remove(mesh_t)
    if mesh_x.users == 0:
        bpy.data.meshes.remove(mesh_x)

    return all_verts, all_faces


def load_reference_object(object_name):
    """
    Appends geometry safely from the internal geometry.blend file using bpy.data.libraries.
    Raises exceptions instead of returning None on failure.
    """
    addon_dir = os.path.dirname(__file__)
    filepath = os.path.join(addon_dir, "geometry", "geometry.blend")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Blend file missing at: {filepath}")

    with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
        if object_name not in data_from.objects:
            raise ValueError(f"Object '{object_name}' not found in geometry.blend")

        data_to.objects = [object_name]

    if not data_to.objects or data_to.objects[0] is None:
        raise RuntimeError(f"Failed to load object '{object_name}'")

    return data_to.objects[0]
