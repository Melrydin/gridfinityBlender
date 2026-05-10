import bpy
import os

import bpy
import os

class GRIDFINITY_OT_batch_export(bpy.types.Operator):
    """Export Gridfinity objects grouped by world location reading direct object names"""
    bl_idname = "gridfinity.batch_export"
    bl_label = "Batch Export Gridfinity"
    bl_options = {'REGISTER'}

    def execute(self, context):
        export_path = bpy.path.abspath(context.scene.gridfinity_export_path)

        if not os.path.exists(export_path):
            self.report({'ERROR'}, "Target directory does not exist")
            return {'CANCELLED'}

        groups = group_gridfinity_objects(bpy.data.objects)
        exported_count = 0

        view_layer = context.view_layer
        orig_active = view_layer.objects.active
        orig_selected = context.selected_objects[:]

        for key, objs in groups.items():
            bpy.ops.object.select_all(action='DESELECT')

            export_name = "Gridfinity_Export"
            for obj in objs:
                obj.select_set(True)
                clean = obj.name.split('.')[0]

                if "Complete" in clean:
                    export_name = clean
                elif "Box" in clean and "Complete" not in export_name:
                    export_name = clean
                elif export_name == "Gridfinity_Export":
                    export_name = clean

            view_layer.objects.active = objs[0]
            full_filepath = os.path.join(export_path, f"{export_name}.stl")

            if hasattr(bpy.ops.wm, "stl_export"):
                bpy.ops.wm.stl_export(filepath=full_filepath, export_selected_objects=True)
            else:
                bpy.ops.export_mesh.stl(filepath=full_filepath, use_selection=True)

            exported_count += 1

        bpy.ops.object.select_all(action='DESELECT')
        for obj in orig_selected:
            try:
                obj.select_set(True)
            except:
                pass
        view_layer.objects.active = orig_active

        self.report({'INFO'}, f"Successfully exported {exported_count} STL files")
        return {'FINISHED'}


def group_gridfinity_objects(objects):
    groups = {}
    for obj in objects:
        if obj.type == 'MESH' and obj.name.lower().startswith("gridfinity"):
            world_loc = obj.matrix_world.to_translation()
            key = (round(world_loc.x, 2), round(world_loc.y, 2))

            if key not in groups:
                groups[key] = []
            groups[key].append(obj)

    return groups


def register():
    bpy.utils.register_class(GRIDFINITY_OT_batch_export)

def unregister():
    bpy.utils.unregister_class(GRIDFINITY_OT_batch_export)
