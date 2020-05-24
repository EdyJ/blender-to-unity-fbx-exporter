bl_info = {
	"name": "Unity FBX format",
	"author": "Angel ""Edy"" Garcia (@VehiclePhysics)",
	"version": (1, 0),
	"blender": (2, 80, 0),
	"location": "File > Export > Unity FBX",
	"description": "FBX exporter compatible with Unity's coordinate and scaling system.",
	"warning": "",
	"wiki_url": "",
	"category": "Import-Export",
}


import bpy
import mathutils
import math


def reset_parent_inverse(ob):
	if (ob.parent):
		mat_world = ob.matrix_world.copy()
		ob.matrix_parent_inverse.identity()
		ob.matrix_basis = ob.parent.matrix_world.inverted() @ mat_world


# Multi-user mesh data is stored here. Unique copies are made for applying the rotation.
# Data for these meshes will be restored after all objects have been processed, so the original shared mesh has also been processed.

mesh_data = dict()


def apply_rotation(ob):
	global mesh_data

	# Create a single copy in multi-user meshes. Will be restored later.
	if (ob.type == "MESH" and ob.data.users > 1):
		mesh_data[ob.name] = ob.data
		ob.data = ob.data.copy()

	# If the object is hidden, unhide it temporarly
	is_hidden = ob.hide_get()
	ob.hide_set(False)

	# Apply rotation
	bpy.ops.object.select_all(action='DESELECT')
	ob.select_set(True)
	bpy.ops.object.transform_apply(rotation = True)

	# Restore original visibility
	ob.hide_set(is_hidden)


def fix_object(ob):
	# Only objects in current view layer
	if ob.name not in bpy.context.view_layer.objects:
		return

	# Reset parent's inverse so we can work with local transform directly
	reset_parent_inverse(ob)

	# Create a copy of the local matrix and set a pure X-90 matrix
	mat_local = ob.matrix_local.copy()
	ob.matrix_local = mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'X')

	# Apply the rotation to the object
	apply_rotation(ob)

	# Reapply the previous local transform with an X+90 rotation
	# https://blender.stackexchange.com/questions/36647/python-low-level-apply-rotation-to-an-object
	ob.matrix_local = mat_local @ mathutils.Matrix.Rotation(math.radians(90.0), 4, 'X')

	# Recursively fix the child objects, as they inherit an X-90 rotation
	for child in ob.children:
		fix_object(child)


def export_unity_fbx(context, filepath, active_collection):
	global mesh_data

	print("Preparing 3D model for Unity...")

	# Root objects: Empty or Mesh without parent and in current view layer
	root_objects = [item for item in bpy.data.objects if ((item.type == "EMPTY" or item.type == "MESH") and not item.parent and item.name in bpy.context.view_layer.objects)]

	# Preserve current scene
	bpy.ops.ed.undo_push()
	mesh_data = dict()

	try:
		# Fix rotations
		for ob in root_objects:
			print(ob.name)
			fix_object(ob)

		# Restore multi-user meshes
		for item in mesh_data:
			bpy.data.objects[item].data = mesh_data[item]

		# Export FBX file
		bpy.ops.export_scene.fbx(filepath=filepath, apply_scale_options='FBX_SCALE_UNITS', object_types={'EMPTY', 'MESH', 'ARMATURE'}, use_active_collection=active_collection)

	except Exception as e:
		bpy.ops.ed.undo()
		print("Errors raised! File not saved.")
		return {'CANCELLED'}

	# Restore scene and finish
	bpy.ops.ed.undo()
	print("FBX file for Unity saved.")
	return {'FINISHED'}


#---------------------------------------------------------------------------------------------------
# Exporter stuff (from the Operator File Export template)

# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ExportUnityFbx(Operator, ExportHelper):
	"""FBX exporter compatible with Unity's coordinate and scaling system"""
	bl_idname = "export_scene.unity_fbx"
	bl_label = "Export Unity FBX"

	# ExportHelper mixin class uses this
	filename_ext = ".fbx"

	filter_glob: StringProperty(
		default="*.fbx",
		options={'HIDDEN'},
		maxlen=255,  # Max internal buffer length, longer would be clamped.
	)

	# List of operator properties, the attributes will be assigned
	# to the class instance from the operator settings before calling.

	active_collection: BoolProperty(
		name="Active Collection Only",
		description="Export only objects from the active collection (and its children)",
		default=False,
	)

	#type: EnumProperty(
	#    name="Example Enum",
	#    description="Choose between two items",
	#    items=(
	#        ('OPT_A', "First Option", "Description one"),
	#        ('OPT_B', "Second Option", "Description two"),
	#    ),
	#    default='OPT_A',
	#)

	def execute(self, context):
		return export_unity_fbx(context, self.filepath, self.active_collection)


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
	self.layout.operator(ExportUnityFbx.bl_idname, text="Unity FBX (.fbx)")


def register():
	bpy.utils.register_class(ExportUnityFbx)
	bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
	bpy.utils.unregister_class(ExportUnityFbx)
	bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
	register()

	# test call
	bpy.ops.export_scene.unity_fbx('INVOKE_DEFAULT')
