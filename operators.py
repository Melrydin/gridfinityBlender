import bpy
import bmesh

class GRIDFINITY_OT_create_container(bpy.types.Operator):
    """Create a new Gridfinity container base unit restricted to 4.75mm height"""
    bl_idname = "gridfinity.create_container"
    bl_label = "Create Gridfinity Base"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        nx = context.scene.gridfinity_x
        ny = context.scene.gridfinity_y

        mesh = bpy.data.meshes.new("Gridfinity_Unit_Mesh")
        obj = bpy.data.objects.new("Gridfinity_Unit", mesh)
        context.collection.objects.link(obj)
        context.view_layer.objects.active = obj
        obj.select_set(True)

        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)

        # Identify vertical edges before scaling to avoid floating point precision issues
        vertical_edges = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 0.5]

        # Scale to correct X and Y but use minimal Z thickness for top face creation
        bmesh.ops.scale(bm, vec=(0.0415, 0.0415, 0.00001), verts=bm.verts)
        bmesh.ops.translate(bm, vec=(0.0, 0.0, 0.00475), verts=bm.verts)

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

        # Merge the micro thickness to create a perfectly flat solid top face
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.00005)

        # Zero out the precise height to align perfectly with the floor
        min_z = min(v.co.z for v in bm.verts)
        bmesh.ops.translate(bm, vec=(0.0, 0.0, -min_z), verts=bm.verts)

        bm.to_mesh(mesh)
        bm.free()
        mesh.update()

        if nx > 1:
            mod_x = obj.modifiers.new(name="Array_X", type='ARRAY')
            mod_x.count = nx
            mod_x.use_relative_offset = False
            mod_x.use_constant_offset = True
            mod_x.constant_offset_displace = (0.043, 0.0, 0.0)
            mod_x.use_merge_vertices = True
            mod_x.merge_threshold = 0.0001
            bpy.ops.object.modifier_apply(modifier="Array_X")

        if ny > 1:
            mod_y = obj.modifiers.new(name="Array_Y", type='ARRAY')
            mod_y.count = ny
            mod_y.use_relative_offset = False
            mod_y.use_constant_offset = True
            mod_y.constant_offset_displace = (0.0, 0.043, 0.0)
            mod_y.use_merge_vertices = True
            mod_y.merge_threshold = 0.0001
            bpy.ops.object.modifier_apply(modifier="Array_Y")

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

        unit_size = 0.0415
        spacing = 0.001
        pitch = unit_size + spacing

        width = unit_size + (nx - 1) * pitch
        depth = unit_size + (ny - 1) * pitch
        height = height_mm * 0.001
        thickness = thickness_mm * 0.001
        base_height = 0.00475

        mesh = bpy.data.meshes.new("Gridfinity_Box_Mesh")
        obj = bpy.data.objects.new("Gridfinity_Box", mesh)
        context.collection.objects.link(obj)
        context.view_layer.objects.active = obj
        obj.select_set(True)

        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)

        bmesh.ops.scale(bm, vec=(width, depth, height), verts=bm.verts)

        offset_x = (nx - 1) * pitch / 2.0
        offset_y = (ny - 1) * pitch / 2.0
        center_z = base_height + (height / 2.0)
        bmesh.ops.translate(bm, vec=(offset_x, offset_y, center_z), verts=bm.verts)

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

        unit_size = 0.0415
        spacing = 0.001
        pitch = unit_size + spacing

        width = unit_size + (nx - 1) * pitch
        depth = unit_size + (ny - 1) * pitch
        height = height_mm * 0.001
        thickness = thickness_mm * 0.001
        base_height = 0.00475
        rim_depth = 0.002

        mesh = bpy.data.meshes.new("Gridfinity_Solid_Box_Mesh")
        obj = bpy.data.objects.new("Gridfinity_Solid_Box", mesh)
        context.collection.objects.link(obj)
        context.view_layer.objects.active = obj
        obj.select_set(True)

        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)

        bmesh.ops.scale(bm, vec=(width, depth, height), verts=bm.verts)

        offset_x = (nx - 1) * pitch / 2.0
        offset_y = (ny - 1) * pitch / 2.0
        center_z = base_height + (height / 2.0)
        bmesh.ops.translate(bm, vec=(offset_x, offset_y, center_z), verts=bm.verts)

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

        self.report({'INFO'}, "Solid Gridfinity box with 2mm rim and inner bevel created.")
        return {'FINISHED'}

class GRIDFINITY_OT_create_basegrid(bpy.types.Operator):
    """Full Gridfinity base profile generation with closed manifold bottom"""
    bl_idname = "gridfinity.create_basegrid"
    bl_label = "Create Basegrid"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mesh = bpy.data.meshes.new("Gridfinity_Basegrid")
        obj = bpy.data.objects.new("Gridfinity_Basegrid", mesh)
        context.collection.objects.link(obj)

        context.view_layer.objects.active = obj
        obj.select_set(True)

        bm = bmesh.new()

        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.021)
        bmesh.ops.bevel(bm, geom=bm.verts, offset=0.008, segments=32, profile=0.5, affect='VERTICES')

        bm.faces.ensure_lookup_table()
        bottom_face = bm.faces[0]

        res = bmesh.ops.extrude_face_region(bm, geom=[bottom_face])
        ext_verts = [v for v in res['geom'] if isinstance(v, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, vec=(0.0, 0.0, 0.005), verts=ext_verts)

        top_face = [f for f in bm.faces if all(v in ext_verts for v in f.verts) and f.normal.z > 0.5][0]

        bmesh.ops.inset_region(bm, faces=[top_face], thickness=0.00215)
        bmesh.ops.translate(bm, vec=(0.0, 0.0, -0.00215), verts=top_face.verts)

        bm.faces.ensure_lookup_table()

        bottom_faces = [f for f in bm.faces if abs(f.calc_center_median().z) < 0.0001]

        bmesh.ops.delete(bm, geom=bottom_faces, context='FACES')

        bm.faces.ensure_lookup_table()

        horizontal_faces = [f for f in bm.faces if abs(f.normal.z) > 0.5]

        if horizontal_faces:

            top_face = max(horizontal_faces, key=lambda f: f.calc_area())

            res = bmesh.ops.extrude_face_region(bm, geom=[top_face])
            ext_verts = [v for v in res['geom'] if isinstance(v, bmesh.types.BMVert)]
            bmesh.ops.translate(bm, vec=(0.0, 0.0, -0.0018), verts=ext_verts)

            bmesh.ops.delete(bm, geom=[top_face], context='FACES')

        horizontal_faces = [f for f in bm.faces if abs(f.normal.z) > 0.5]

        if horizontal_faces:

            top_face = max(horizontal_faces, key=lambda f: f.calc_area())

            res = bmesh.ops.extrude_face_region(bm, geom=[top_face])
            ext_verts = [v for v in res['geom'] if isinstance(v, bmesh.types.BMVert)]
            current_z = ext_verts[0].co.z
            bmesh.ops.translate(bm, vec=(0.0, 0.0, -current_z), verts=ext_verts)

            bmesh.ops.delete(bm, geom=[top_face], context='FACES')

        bm.faces.ensure_lookup_table()
        bm.normal_update()

        horizontal_faces = [f for f in bm.faces if abs(f.normal.z) > 0.5]

        if horizontal_faces:
            top_face = max(horizontal_faces, key=lambda f: f.calc_area())

            inner_edges = [e for e in top_face.edges if e.calc_length() < 0.040]

            bmesh.ops.bevel(
                bm,
                geom=inner_edges,
                offset=0.0008,
                segments=1,
                profile=0.5,
                affect='EDGES'
            )

        horizontal_faces = [f for f in bm.faces if abs(f.normal.z) > 0.5]

        if horizontal_faces:
            top_face = max(horizontal_faces, key=lambda f: f.calc_area())
            bmesh.ops.delete(bm, geom=[top_face], context='FACES')

        bm.edges.ensure_lookup_table()
        bottom_edges = [e for e in bm.edges if abs(e.verts[0].co.z) < 0.0001 and abs(e.verts[1].co.z) < 0.0001]

        if len(bottom_edges) > 0:
            bmesh.ops.bridge_loops(bm, edges=bottom_edges)

        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

        bm.to_mesh(mesh)
        bm.free()
        mesh.update()

        self.report({'INFO'}, "Gridfinity Basegrid perfectly hollowed and bridged.")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(GRIDFINITY_OT_create_container)
    bpy.utils.register_class(GRIDFINITY_OT_create_box)
    bpy.utils.register_class(GRIDFINITY_OT_create_solid_box)
    bpy.utils.register_class(GRIDFINITY_OT_create_basegrid)


def unregister():
    bpy.utils.unregister_class(GRIDFINITY_OT_create_container)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_box)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_solid_box)
    bpy.utils.unregister_class(GRIDFINITY_OT_create_basegrid)
