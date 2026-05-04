"""
Gridfinity Blender Addon
A Blender addon for creating and managing Gridfinity storage containers
"""

bl_info = {
    "name": "Gridfinity",
    "blender": (4, 5, 0),
    "category": "Object",
    "version": (0, 1, 0),
    "author": "Clemens",
    "description": "Create and manage Gridfinity storage containers in Blender",
    "location": "View 3D > Sidebar > Gridfinity",
    "support": "COMMUNITY",
}

import bpy
from . import ui, operators


# Module registration
def register():
    """Register addon classes and properties"""
    operators.register()
    ui.register()
    print(f"✓ {bl_info['name']} addon registered (v{'.'.join(map(str, bl_info['version']))})")


def unregister():
    """Unregister addon classes and properties"""
    ui.unregister()
    operators.unregister()
    print(f"✗ {bl_info['name']} addon unregistered")


if __name__ == "__main__":
    register()
