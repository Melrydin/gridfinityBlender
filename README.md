# Gridfinity Generator for Blender

<div align="center">

A powerful Blender addon for procedurally generating precise, modular, and customizable Gridfinity storage components with advanced geometry merging and boolean operations for exact drawer fitting.

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Releases](https://github.com/clemens/gridfinityBlender/releases) • [License](#license)

</div>

## Overview

This addon streamlines the creation of professional-grade Gridfinity storage components directly within Blender. Whether you're designing custom organizers, fitting components into existing drawers, or batch-exporting for 3D printing, this tool provides precise control and automated workflows.

**Key Capabilities:**
- 🎨 Procedural component generation with real-time parameter adjustments
- 📏 Millimeter-precise dimensions for perfect drawer fits
- 🔄 Smart boolean operations for seamless geometry merging
- 📦 Batch STL export with intelligent grouping
- 🔌 Full compatibility with Blender 4.1+ and legacy versions

## Origin and Source

The Gridfinity organizational system was invented by Zack Freedman. Discover more about the system and find additional designs on his [Thangs profile](https://thangs.com/designer/ZackFreedman).

## Requirements

- **Blender 3.6+** (Blender 4.1+ recommended for optimal STL export performance)
- **Python 3.10+** (included with Blender)
- **~50 MB** disk space for addon and dependencies

## Features

### 🎯 Configuration & Customization

#### Dimension Settings
- **Grid Size:** Define the exact number of 42mm base units in X and Y directions
- **Bin Parameters:** Customize total bin height and wall thickness (in millimeters)
- **Drawer Constraints:** Specify maximum drawer dimensions for precise fitting
- **Real-time Preview:** Adjust parameters and see changes instantly

### 🏗️ Gridfinity Components

#### Complete Generation Modes
- **Baseplate + Hollow Bin:** Unified object with standard baseplate and hollow storage bin
- **Baseplate + Solid Bin:** Unified object with baseplate and solid block (includes stacking rim)

#### Drawer Fit Mode
The intelligent fitting system automatically:
- Calculates maximum integer grid units fitting within drawer constraints
- Generates perfectly aligned baseplates
- Uses precise boolean intersection to cut edges to exact millimeter limits
- Preserves unit integrity and origin points

#### Standalone Components
- **Baseplate Only:** Single flat array at standard 4.75mm height
- **Stacking Lip Array:** Procedurally generated stacking profiles with optimized topology
- **Hollow Bin Only:** Raw bin walls and inner bottom bevel (baseplate-free)
- **Solid Bin Only:** Solid block with stacking rim (baseplate-free)

### 📤 Export Utilities

#### Intelligent Batch Export
- **One-Click STL Export:** Export all generated objects simultaneously
- **Smart Grouping:** Automatically merges overlapping components based on geometric centers
- **Auto Naming:** Descriptive filenames generated without manual input
- **API Compatibility:** Seamlessly switches between native C++ (Blender 4.1+) and legacy Python exporters

## Installation

### Method 1: From GitHub (Recommended)
1. Download the latest release as a `.zip` file from the [Releases page](https://github.com/clemens/gridfinityBlender/releases)
2. In Blender, navigate to **Edit → Preferences → Add-ons**
3. Click **Install** and select the downloaded ZIP file
4. Search for "Gridfinity" and enable the addon by checking the box
5. The Gridfinity panel will appear in the 3D Viewport sidebar

### Method 2: From Source
1. Clone the repository or download as ZIP
2. Extract to your Blender addons folder:
   - **Windows:** `%APPDATA%\Blender Foundation\Blender\<version>\scripts\addons`
   - **macOS:** `~/Library/Application Support/Blender/<version>/scripts/addons`
   - **Linux:** `~/.config/blender/<version>/scripts/addons`
3. Restart Blender and enable the addon in Preferences

## Usage

### Getting Started

1. **Open the Panel**
   - Open the 3D Viewport in Blender
   - Press `N` to toggle the sidebar
   - Navigate to the **Gridfinity** tab

2. **Set Your Dimensions**
   - Enter **Grid Size** (number of 42mm units in X and Y)
   - Customize **Bin Height** and **Wall Thickness** (millimeters)
   - Optionally set **Drawer Constraints** for fitted generation

3. **Generate Components**
   - Select your desired generation mode
   - Click the corresponding button
   - Generated objects appear in the viewport

### Workflow Examples

#### Creating a Fitted Drawer Organizer
1. Measure your drawer: 300mm × 200mm × 80mm
2. Set **Drawer Constraints** to these dimensions
3. Click **Generate Fitted Grid**
4. Adjust fine details if needed
5. Export to STL with a single click

#### Batch Exporting Multiple Components
1. Generate several different Gridfinity components in your scene
2. Navigate to **Export Utilities**
3. Click **Batch Export STL**
4. Select export directory
5. All components are automatically named and grouped

## Advanced Features

### Magnet Baseplate Support
Full support for magnetic baseplate configurations enables compatible components with magnetic organizing systems.

### Geometry Optimization
- Automatic vertex merging for clean topology
- Internal wall removal for 3D printing efficiency
- Precise beveling on outer corners for manifold meshes

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Addon not appearing after install | Restart Blender completely |
| Export produces invalid STL | Ensure Blender 4.1+ or check Python exporter compatibility |
| Generated geometry looks corrupted | Reset parameters to defaults and regenerate |
| Boolean operations fail | Increase wall thickness or check for overlapping geometry |

## License

This addon is provided under the terms specified in the [LICENSE](LICENSE) file.

## Support & Contributions

- **Report Issues:** Please use the [GitHub Issues](https://github.com/clemens/gridfinityBlender/issues) page
- **Feature Requests:** Share your ideas through GitHub Issues
- **Contributions:** Pull requests are welcome!

---

**Created by:** Clemens
**Last Updated:** May 2026
**Blender Compatibility:** 3.6 - Latest
