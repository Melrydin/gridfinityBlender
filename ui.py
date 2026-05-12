import bpy

class VIEW3D_PT_gridfinity_panel(bpy.types.Panel):
    bl_label = "Gridfinity Generator"
    bl_idname = "VIEW3D_PT_gridfinity"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Gridfinity'

    def draw(self, context):
        layout = self.layout
        props = context.scene.gridfinity

        box_unit = layout.box()
        box_unit.label(text="Grid Size", icon='OBJECT_DATAMODE')
        row = box_unit.row()
        row.prop(props, "x", text="Width X")
        row.prop(props, "y", text="Depth Y")

        box_unit.prop(props, "use_magnets", text="Add Magnet Holders")
        box_unit.prop(props, "use_infill", text="Solid Baseplate Infill")

        layout.separator()

        box_ui = layout.box()
        box_ui.label(text="Complete Gridfinity", icon='PACKAGE')
        box_ui.prop(props, "bin_height", text="Bin Height mm")
        box_ui.prop(props, "bin_wall_thickness", text="Wall Thickness mm")
        box_ui.operator("gridfinity.create_baseplate_with_bin", text="Baseplate + Hollow Bin", icon='PACKAGE')
        box_ui.operator("gridfinity.create_baseplate_with_solid_bin", text="Baseplate + Solid Bin", icon='CUBE')

        layout.separator()

        box_drawer = layout.box()
        box_drawer.label(text="Drawer Fit Mode", icon='VIEW_ORTHO')
        col = box_drawer.column(align=True)
        col.prop(props, "drawer_x", text="Max Drawer Width X")
        col.prop(props, "drawer_y", text="Max Drawer Depth Y")
        box_drawer.operator("gridfinity.create_drawer_fitted_grid", text="Generate Fitted Grid")

        layout.separator()

        box_lid = layout.box()
        box_lid.label(text="Lid Generator", icon='MOD_SOLIDIFY')
        box_lid.prop(props, "lid_thickness", text="Lid Thickness mm")
        box_lid.prop(props, "lid_tolerance", text="Tolerance mm")
        box_lid.operator("gridfinity.create_lid", text="Create Fitted Lid", icon='MESH_PLANE')

        layout.separator()

        box_comp = layout.box()
        box_comp.label(text="Standalone Components")
        box_comp.operator("gridfinity.create_baseplate", text="Baseplate Only")
        box_comp.operator("gridfinity.create_stacking_lip_array", text="Stacking Lip Array")
        box_comp.operator("gridfinity.create_bin", text="Hollow Bin Only")
        box_comp.operator("gridfinity.create_solid_bin", text="Solid Bin Only")

        layout.separator()

        box_export = layout.box()
        box_export.label(text="Export Utilities", icon='EXPORT')
        box_export.prop(props, "export_path", text="Folder")
        box_export.operator("gridfinity.batch_export", text="Batch Export STL", icon='MESH_CUBE')

def register():
    bpy.utils.register_class(VIEW3D_PT_gridfinity_panel)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_gridfinity_panel)
