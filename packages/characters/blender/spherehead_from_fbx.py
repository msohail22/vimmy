import bpy
from pathlib import Path
from mathutils import Vector


BASE_DIR = Path('/home/sohail/Github/vimmy/packages/characters')
SOURCE_FBX = Path('/home/sohail/Downloads/Ch36_nonPBR.fbx')
OUTPUT_PATH = BASE_DIR / 'assets' / 'spherehead_mannequin.glb'

HEAD_BONE = 'mixamorig1:Head'
NECK_BONE = 'mixamorig1:Neck'


def reset_scene():
	bpy.ops.object.select_all(action='SELECT')
	bpy.ops.object.delete(use_global=False)
	for collection in (bpy.data.meshes, bpy.data.materials, bpy.data.textures, bpy.data.images):
		for block in list(collection):
			if block.users == 0:
				collection.remove(block)


def ensure_dirs():
	OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def import_base():
	bpy.ops.import_scene.fbx(filepath=str(SOURCE_FBX))
	armature = next(obj for obj in bpy.data.objects if obj.type == 'ARMATURE')
	mesh = next(obj for obj in bpy.data.objects if obj.type == 'MESH')
	return armature, mesh


def make_material(name, color, roughness=0.8):
	mat = bpy.data.materials.new(name=name)
	mat.use_nodes = True
	bsdf = mat.node_tree.nodes['Principled BSDF']
	bsdf.inputs['Base Color'].default_value = color
	bsdf.inputs['Roughness'].default_value = roughness
	bsdf.inputs['Specular IOR Level'].default_value = 0.3
	return mat


def assign_body_material(mesh):
	body_mat = make_material('SphereBody', (0.24, 0.25, 0.31, 1.0), roughness=0.88)
	mesh.data.materials.clear()
	mesh.data.materials.append(body_mat)


def slim_and_pose_body(armature, mesh):
	bpy.context.view_layer.objects.active = armature
	bpy.ops.object.mode_set(mode='POSE')
	pose_updates = {
		'mixamorig1:LeftArm': (0.0, 0.0, -0.15),
		'mixamorig1:RightArm': (0.0, 0.0, 0.15),
		'mixamorig1:LeftForeArm': (0.0, 0.0, -0.08),
		'mixamorig1:RightForeArm': (0.0, 0.0, 0.08),
	}
	for bone_name, rot in pose_updates.items():
		bone = armature.pose.bones.get(bone_name)
		if bone:
			bone.rotation_mode = 'XYZ'
			bone.rotation_euler = rot
	bpy.ops.object.mode_set(mode='OBJECT')

	# Nudge the original head geometry inward so the sphere reads cleanly.
	head_group = mesh.vertex_groups.get(HEAD_BONE)
	neck_group = mesh.vertex_groups.get(NECK_BONE)
	if not head_group:
		return

	head_indices = set()
	neck_indices = set()
	for vertex in mesh.data.vertices:
		for group in vertex.groups:
			if group.group == head_group.index and group.weight > 0.35:
				head_indices.add(vertex.index)
			if neck_group and group.group == neck_group.index and group.weight > 0.35:
				neck_indices.add(vertex.index)

	if not head_indices:
		return

	bpy.context.view_layer.objects.active = mesh
	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.select_mode(type='VERT')
	bpy.ops.mesh.select_all(action='DESELECT')
	bpy.ops.object.mode_set(mode='OBJECT')

	coords = [mesh.data.vertices[i].co.copy() for i in head_indices]
	center = sum(coords, Vector()) / len(coords)
	for vertex in mesh.data.vertices:
		if vertex.index in head_indices:
			vertex.select = True
			offset = vertex.co - center
			vertex.co = center + offset * 0.2
		elif vertex.index in neck_indices:
			vertex.select = True
			offset = vertex.co - center
			vertex.co = center + offset * 0.72

	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.remove_doubles(threshold=0.0001)
	bpy.ops.object.mode_set(mode='OBJECT')


def create_head_sphere(armature):
	head_bone = armature.pose.bones[HEAD_BONE]
	head_world = armature.matrix_world @ head_bone.head
	tail_world = armature.matrix_world @ head_bone.tail
	radius = max((tail_world - head_world).length * 1.55, 0.16)
	center = head_world.lerp(tail_world, 0.6) + Vector((0.0, 0.0, radius * 0.18))

	bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=radius, location=center)
	head = bpy.context.active_object
	head.name = 'SphereheadOrb'

	subdiv = head.modifiers.new(name='Subsurf', type='SUBSURF')
	subdiv.levels = 1
	subdiv.render_levels = 1
	bpy.context.view_layer.objects.active = head
	bpy.ops.object.shade_smooth()
	bpy.ops.object.modifier_apply(modifier=subdiv.name)

	dark_mat = make_material('SphereHeadDark', (0.28, 0.29, 0.36, 1.0), roughness=0.96)
	light_mat = make_material('SphereHeadLight', (0.92, 0.92, 0.9, 1.0), roughness=0.98)
	head.data.materials.clear()
	head.data.materials.append(dark_mat)
	head.data.materials.append(light_mat)

	for poly in head.data.polygons:
		z_avg = sum(head.data.vertices[i].co.z for i in poly.vertices) / len(poly.vertices)
		poly.material_index = 1 if z_avg > radius * 0.48 else 0

	mod = head.modifiers.new(name='Armature', type='ARMATURE')
	mod.object = armature
	vg = head.vertex_groups.new(name=HEAD_BONE)
	vg.add([vertex.index for vertex in head.data.vertices], 1.0, 'ADD')
	head.parent = armature
	head.parent_type = 'OBJECT'

	return head


def center_character(objects):
	min_z = None
	for obj in objects:
		if obj.type != 'MESH':
			continue
		for vertex in obj.data.vertices:
			world = obj.matrix_world @ vertex.co
			min_z = world.z if min_z is None else min(min_z, world.z)
	if min_z is None:
		return
	for obj in objects:
		obj.location.z -= min_z


def export_glb(objects):
	bpy.ops.object.select_all(action='DESELECT')
	for obj in objects:
		obj.select_set(True)
	bpy.context.view_layer.objects.active = objects[0]
	bpy.ops.export_scene.gltf(
		filepath=str(OUTPUT_PATH),
		use_selection=True,
		export_format='GLB',
		export_apply=False,
		export_animations=False,
		export_yup=True,
	)


def main():
	ensure_dirs()
	reset_scene()
	armature, mesh = import_base()
	assign_body_material(mesh)
	slim_and_pose_body(armature, mesh)
	head = create_head_sphere(armature)
	center_character([armature, mesh, head])
	export_glb([armature, mesh, head])


if __name__ == '__main__':
	main()
