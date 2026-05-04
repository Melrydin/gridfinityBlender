"""
UI panels for Gridfinity addon
"""

import bpy
from bpy.types import Panel


class GRIDFINITY_PT_main_panel(Panel):
    """Main Gridfinity panel in 3D View sidebar"""
    bl_label = "Gridfinity"
    bl_idname = "GRIDFINITY_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Gridfinity'

    def draw(self, context):
        layout = self.layout

        # Title
        layout.label(text="Gridfinity Storage Creator", icon='CUBE')

        # Separator
        layout.separator()

        # Main button to create container
        layout.operator(
            "gridfinity.create_container",
            text="Create Container",
            icon='ADD'
        )

        layout.separator()

        # Info section
        box = layout.box()
        box.label(text="Info", icon='INFO')
        box.label(text="Click 'Create Container' to get started")


# List of all panels
classes = [
    GRIDFINITY_PT_main_panel,
]


def register():
    """Register all panel classes"""
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    """Unregister all panel classes"""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
