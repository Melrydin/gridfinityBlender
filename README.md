# Gridfinity Generator for Blender

This addon for Blender procedurally generates precise, clean, and modular components for the Gridfinity storage system. It features advanced geometry merging and boolean operations for exact drawer fitting.

## Origin and Source
The Gridfinity organizational system was invented by Zack Freedman. You can find his original designs and further information on his Thangs profile: https://thangs.com/designer/ZackFreedman

## Features

### 1. Dimension Settings
* **Grid Size:** Define the exact number of 42mm base units in X and Y directions.
* **Bin Parameters:** Customize the total bin height and wall thickness in millimeters.
* **Drawer Constraints:** Specify exact maximum drawer dimensions in millimeters for custom fitting.

### 2. Complete Gridfinity Generation
* **Baseplate + Hollow Bin:** Generates a unified object containing the standard baseplate with a hollow bin on top.
* **Baseplate + Solid Bin:** Generates a unified object containing the standard baseplate with a solid block bin (includes top stacking rim).

### 3. Drawer Fit Mode
* **Generate Fitted Grid:** Automatically calculates the maximum possible integer grid units that fit within your specific drawer dimensions. It generates the baseplate array and uses precise boolean intersection to cut the far edges exactly to your millimeter limits while keeping the origin units perfectly intact.

### 4. Standalone Components
* **Baseplate Only:** Generates a flat baseplate array strictly limited to the standard 4.75mm height profile.
* **Stacking Lip Array:** Procedurally generates the top stacking lip profile. Automatically merges inner vertices, removes internal walls, and strictly bevels the four outer corners for perfect topological manifolds.
* **Hollow Bin Only:** Generates the raw bin walls and inner bottom bevel without the baseplate.
* **Solid Bin Only:** Generates a solid block bin with the top stacking rim without the baseplate.

### 5. Export Utilities
* **Batch Export STL:** A one click export solution for all generated Gridfinity objects in the current scene.
* **Smart Grouping:** Automatically merges overlapping components like a baseplate and a bin into a single STL file based on their exact geometric center.
* **Auto Naming:** Generates descriptive filenames automatically without requiring manual input.
* **Modern API Support:** Dynamically switches between the native C++ STL exporter in Blender 4.1 and newer and the legacy Python exporter for older versions.

## Installation
1. Pack the addon folder into a ZIP archive.
2. Open Blender and navigate to Edit > Preferences > Addons.
3. Click Install and select your ZIP archive.
4. Enable the module by checking the box next to its name.

## Usage
1. Open the 3D Viewport in Blender.
2. Press N to open the sidebar.
3. Navigate to the Gridfinity tab.
4. Adjust your dimensions in the corresponding panels.
5. Click the desired generation button.
