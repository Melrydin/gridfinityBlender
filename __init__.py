bl_info = {
    "name": "Gridfinity Generator",
    "author": "Melrydin",
    "version": (0, 1, 3),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > Gridfinity",
    "description": "Generates customizable Gridfinity storage solutions",
    "category": "Object",
    "license": "GPL-3.0-or-later",

}

from . import properties
from . import operators
from . import ui
from . import exporter

def register():
    properties.register()
    operators.register()
    ui.register()
    exporter.register()

def unregister():
    ui.unregister()
    operators.unregister()
    properties.unregister()
    exporter.unregister()
