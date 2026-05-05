bl_info = {
    "name": "Gridfinity Base Generator",
    "author": "Melrydin",
    "version": (0, 1, 1),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > Gridfinity",
    "description": "Generates customizable Gridfinity baseplates",
    "category": "Object",
}

import bpy
from . import properties
from . import operators
from . import ui

def register():
    properties.register()
    operators.register()
    ui.register()

def unregister():
    ui.unregister()
    operators.unregister()
    properties.unregister()
