
# Blender To Unity FBX Exporter

FBX exporter add-on for Blender 2.80+ compatible with Unity's coordinate and scaling system. Exported FBX files are imported into Unity with the correct rotations and scales.

## How to install

1. Clone the repository or download the add-on file [`blender-to-unity-fbx-exporter.py`](/blender-to-unity-fbx-exporter.py) to your device.
2. In Blender go to Edit > Preferences > Add-ons, then use the Install… button and use the File Browser to select the add-on file.
3. Enable the add-on by checking the enable checkbox.

<p align="center">
<img src="/img/blender-to-unity-fbx-exporter-addon.png" alt="Blender To Unity FBX Exporter Add-On">
</p>

## How to use

**File > Export > Unity FBX (.fbx)**

Exports all Empty, Mesh and Armature objects in the current scene except those in excluded collections. The full hierarchy is properly preserved and exported, including local positions and rotations.

<p align="center">
<img src="/img/blender-to-unity-fbx-exporter-menu.png" alt="Blender To Unity FBX Exporter Menu">
</p>

The File Browser exposes options to export the active collection only and/or the selected objects only. If both options are checked then only the selected objects in the active collection are exported.

<p align="center">
<img src="/img/blender-to-unity-fbx-exporter-options.png" alt="Blender To Unity FBX Exporter Options">
</p>

## How it works

The exporter modifies the objects in the Blender scene right before exporting the FBX file, then reverts the modifications afterwards.

Every object to be exported receives a rotation of +90 degrees around the X axis in their transform _without_ actually modifying the visual pose of its geometry and children. This is done in the root objects, then recursively propagated to their children (as they inherit a -90 rotation after transforming their parent). The modified scene is then exported to FBX using Blender's built-in FBX exporter with the proper options applied. Finally the scene is restored to the state before the modifications.

When Unity imports the FBX file all objects receive a rotation of -90 degrees in the X axis to preserve their visual pose. As the objects in the FBX already have a rotation of X+90 then the undesired rotation is canceled and everything gets imported correctly.

#### Why not use the "Experimental - Apply Transform" option?

This option doesn't work with object hierarchies of more than 2 levels. Objects beyond the 2nd level keep receiving unwanted rotations and scalings when imported into Unity.

## Notes

- Not tested with armatures nor animations. Feel free to open an issue with a simple repro scene if you encounter any problem.
- Negative scales are imported with an unexpected but equivalent transform. Example: scale (-1, 1, 1) and no rotation is imported as scale (-1, -1, -1) and rotation (-180, 0, 0). This is equivalent, and may be changed to, the original scale (-1, 1, 1) and rotation (0, 0, 0) in Unity.

#### Tested:

- Mixed EMPTY and MESH hierarchies with depth > 3
- Local rotations
- Non-uniform scaling
- Multi-user meshes, with and without modifiers
- Partial selections (Selected Objects Only)
- Hidden objects and collections (eye icon in the outliner).
- Disabled objects (monitor icon in the outliner). Imported with MeshRenderer disabled in Unity.
- Disabled collections (monitor icon in the outliner).
- Excluded collections (unchecked in the outliner). Won't be exported.
- Nested collections
- Objects with their parent in a disabled/excluded collection
- Mesh modifiers

## About the author

Angel "Edy" Garcia<br>
[@VehiclePhysics](https://twitter.com/VehiclePhysics)<br>
https://vehiclephysics.com
