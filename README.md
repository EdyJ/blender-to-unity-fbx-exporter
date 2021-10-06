
# Blender To Unity FBX Exporter

FBX exporter add-on for Blender 2.80+ compatible with Unity's coordinate and scaling system. Exported FBX files are imported into Unity with the correct rotations and scales.

## How to install

1. Clone the repository or download the add-on file [`blender-to-unity-fbx-exporter.py`](https://raw.githubusercontent.com/EdyJ/blender-to-unity-fbx-exporter/master/blender-to-unity-fbx-exporter.py) to your device.
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

The File Browser exposes selection and armature options:

<p align="center">
<img src="/img/blender-to-unity-fbx-exporter-options.png" alt="Blender To Unity FBX Exporter Options">
</p>

## How it works

The exporter modifies the objects in the Blender scene right before exporting the FBX file, then reverts the modifications afterwards.

Every object to be exported receives a rotation of +90 degrees around the X axis in their transform _without_ actually modifying the visual pose of its geometry and children. This is done in the root objects, then recursively propagated to their children (as they inherit a -90 rotation after transforming their parent). The modified scene is then exported to FBX using Blender's built-in FBX exporter with the proper options applied. Finally the scene is restored to the state before the modifications.

When Unity imports the FBX file all objects receive a rotation of -90 degrees in the X axis to preserve their visual pose. As the objects in the FBX already have a rotation of X+90 then the undesired rotation is canceled and everything gets imported correctly.

#### Why not use the "Experimental - Apply Transform" option of the default FBX Exporter?

This option doesn't work with object hierarchies of more than 2 levels. Objects beyond the 2nd level keep receiving unwanted rotations and scalings when imported into Unity.

#### Why not import the .blend file directly in the Unity project?

Requires Blender to be installed in the system, so:

- it's a no-go for publishing packages in the Asset Store.
- .blend files don't work with Unity Cloud Build.

## Known issues

- Negative scaling is imported with a different but equivalent transform in Unity. Example: scale (-1, 1, 1) and no rotation is imported as scale (-1, -1, -1) and rotation (-180, 0, 0). In Unity this is equivalent, and may be changed to, the original scale (-1, 1, 1) and rotation (0, 0, 0).
- Child objects in instanced collections receive an unneeded 90 degrees rotation in the X axis. Clearing this rotation in Unity gives the expected result. ([#3](https://github.com/EdyJ/blender-to-unity-fbx-exporter/issues/3))
- Exporting right after deleting an object throws an exception. Workaround: select some object before exporting. ([#17](https://github.com/EdyJ/blender-to-unity-fbx-exporter/issues/17))

#### Tested and working:

- Mixed EMPTY and MESH hierarchies with depth > 3.
- Local rotations are preserved.
- Non-uniform scaling.
- Mesh modifiers.
- Multi-user meshes and linked objects, with and without modifiers.
- Armatures and Armature modifier.
- Partial selections (Selected Objects Only).
- Hidden objects and collections (eye icon in the outliner).
- Disabled objects (monitor icon in the outliner). Imported with MeshRenderer disabled in Unity.
- Disabled collections (monitor icon in the outliner).
- Excluded collections (unchecked in the outliner). Won't be exported.
- Nested collections.
- Objects with their parent in a disabled/excluded collection.

## About the author

Angel "Edy" Garcia<br>
[@VehiclePhysics](https://twitter.com/VehiclePhysics)<br>
https://vehiclephysics.com
