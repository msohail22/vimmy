import bpy
from math import radians
from pathlib import Path


SCRIPT_PATH = Path(bpy.data.filepath) if bpy.data.filepath else None
BASE_DIR = SCRIPT_PATH.parent.parent if SCRIPT_PATH else Path.cwd()
ASSET_DIR = BASE_DIR / 'assets'
BLEND_DIR = BASE_DIR / 'blender'
OUTPUT_PATH = ASSET_DIR / 'spherehead_isometric.glb'


def reset_scene():
	bpy.ops.object.select_all(action='SELECT')
	bpy.ops.object.delete(use_global=False)
	for block in bpy.data.meshes:
		if block.users == 0:
			bpy.data.meshes.remove(block)
	for block in bpy.data.materials:
		if block.users == 0:
			bpy.data.materials.remove(block)


def ensure_dirs():
	ASSET_DIR.mkdir(parents=True, exist_ok=True)
	BLEND_DIR.mkdir(parents=True, exist_ok=True)


def make_material(name, base_color, roughness=0.65):
	mat = bpy.data.materials.new(name=name)
	mat.use_nodes = True
	bsdf = mat.node_tree.nodes['Principled BSDF']
	bsdf.inputs['Base Color'].default_value = base_color
	bsdf.inputs['Roughness'].default_value = roughness
	bsdf.inputs['Specular IOR Level'].default_value = 0.35
	return mat


def apply_transforms(obj):
	bpy.context.view_layer.objects.active = obj
	obj.select_set(True)
	bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
	obj.select_set(False)


def add_metaball(name, location, scale, rotation=(0.0, 0.0, 0.0)):
	bpy.ops.object.metaball_add(type='BALL', location=location)
	obj = bpy.context.active_object
	obj.name = name
	obj.rotation_euler = rotation
	obj.scale = scale
	obj.data.resolution = 0.18
	obj.data.render_resolution = 0.08
	obj.data.threshold = 0.6
	return obj


def build_body():
	parts = []
	parts.append(add_metaball('TorsoUpper', (0.0, 0.0, 1.65), (0.62, 0.44, 0.54)))
	parts.append(add_metaball('TorsoMid', (0.0, 0.0, 1.3), (0.5, 0.34, 0.48)))
	parts.append(add_metaball('Pelvis', (0.0, 0.0, 0.96), (0.42, 0.28, 0.3)))

	for side in (-1, 1):
		x = 0.24 * side
		parts.append(add_metaball(f'Chest_{side}', (x, 0.05, 1.46), (0.26, 0.2, 0.24)))
		parts.append(add_metaball(f'ObliqueTop_{side}', (x * 0.92, 0.02, 1.18), (0.18, 0.14, 0.14)))
		parts.append(add_metaball(f'ObliqueMid_{side}', (x * 0.78, 0.02, 1.0), (0.16, 0.12, 0.12)))
		parts.append(add_metaball(f'Shoulder_{side}', (0.48 * side, 0.0, 1.7), (0.22, 0.18, 0.2)))
		parts.append(add_metaball(f'Bicep_{side}', (0.66 * side, 0.0, 1.35), (0.18, 0.18, 0.34), (0.0, radians(9 * -side), 0.0)))
		parts.append(add_metaball(f'Forearm_{side}', (0.72 * side, 0.0, 0.99), (0.13, 0.13, 0.32), (0.0, radians(4 * -side), 0.0)))
		parts.append(add_metaball(f'Hand_{side}', (0.74 * side, 0.0, 0.68), (0.1, 0.08, 0.12)))
		parts.append(add_metaball(f'Glute_{side}', (0.18 * side, -0.06, 0.84), (0.18, 0.16, 0.18)))
		parts.append(add_metaball(f'Thigh_{side}', (0.18 * side, 0.0, 0.42), (0.18, 0.18, 0.44)))
		parts.append(add_metaball(f'Calf_{side}', (0.16 * side, 0.0, 0.0), (0.14, 0.14, 0.38), (radians(2), 0.0, 0.0)))
		parts.append(add_metaball(f'Foot_{side}', (0.16 * side, 0.1, -0.38), (0.14, 0.22, 0.08), (radians(82), 0.0, 0.0)))

	root = parts[0]
	for obj in parts[1:]:
		obj.data = root.data

	for obj in parts:
		obj.select_set(True)
	bpy.context.view_layer.objects.active = root
	bpy.ops.object.convert(target='MESH')
	body = bpy.context.active_object
	body.name = 'SphereheadBody'

	body.select_set(True)
	bpy.ops.object.shade_smooth()
	mod = body.modifiers.new(name='Remesh', type='REMESH')
	mod.mode = 'SMOOTH'
	mod.octree_depth = 6
	mod.scale = 0.92
	mod.use_smooth_shade = True
	bpy.context.view_layer.objects.active = body
	bpy.ops.object.modifier_apply(modifier=mod.name)

	subdiv = body.modifiers.new(name='Subsurf', type='SUBSURF')
	subdiv.levels = 1
	subdiv.render_levels = 1
	bpy.ops.object.modifier_apply(modifier=subdiv.name)

	decimate = body.modifiers.new(name='Decimate', type='DECIMATE')
	decimate.ratio = 0.72
	bpy.ops.object.modifier_apply(modifier=decimate.name)

	bpy.ops.object.mode_set(mode='EDIT')
	bpy.ops.mesh.select_all(action='SELECT')
	bpy.ops.mesh.normals_make_consistent(inside=False)
	bpy.ops.mesh.remove_doubles(threshold=0.0005)
	bpy.ops.object.mode_set(mode='OBJECT')
	body.select_set(False)
	return body


def build_head():
	bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=0.54, location=(0.0, 0.0, 2.52))
	head = bpy.context.active_object
	head.name = 'SphereheadHead'
	head.scale[1] = 1.02
	apply_transforms(head)
	bpy.ops.object.shade_smooth()

	displace = head.modifiers.new(name='HeadNoise', type='DISPLACE')
	texture = bpy.data.textures.new('HeadTexture', type='CLOUDS')
	texture.noise_scale = 0.16
	texture.noise_depth = 2
	displace.texture = texture
	displace.strength = 0.025
	bpy.context.view_layer.objects.active = head
	bpy.ops.object.modifier_apply(modifier=displace.name)

	return head


def add_neck():
	bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.14, depth=0.32, location=(0.0, 0.0, 2.0))
	neck = bpy.context.active_object
	neck.name = 'SphereheadNeck'
	bpy.ops.object.shade_smooth()
	return neck


def join_meshes(objects, name):
	bpy.ops.object.select_all(action='DESELECT')
	for obj in objects:
		obj.select_set(True)
	bpy.context.view_layer.objects.active = objects[0]
	bpy.ops.object.join()
	joined = bpy.context.active_object
	joined.name = name
	return joined


def set_origin_to_feet(obj):
	bpy.context.view_layer.objects.active = obj
	bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
	min_z = min((obj.matrix_world @ v.co).z for v in obj.data.vertices)
	obj.location.z -= min_z


def assign_materials(character, body_material, head_material):
	mesh = character.data
	mesh.materials.clear()
	mesh.materials.append(body_material)
	mesh.materials.append(head_material)

	head_group = character.vertex_groups.new(name='HeadMask')
	for vertex in mesh.vertices:
		if vertex.co.z > 2.12:
			head_group.add([vertex.index], 1.0, 'ADD')

	for poly in mesh.polygons:
		if all(mesh.vertices[idx].co.z > 2.12 for idx in poly.vertices):
			poly.material_index = 1
		else:
			poly.material_index = 0


def finalize_mesh(obj):
	bpy.context.view_layer.objects.active = obj
	mod = obj.modifiers.new(name='Triangulate', type='TRIANGULATE')
	bpy.ops.object.modifier_apply(modifier=mod.name)
	obj.rotation_euler = (0.0, 0.0, 0.0)
	obj.location = (0.0, 0.0, 0.0)
	obj.scale = (1.0, 1.0, 1.0)


def export_glb(obj):
	bpy.ops.object.select_all(action='DESELECT')
	obj.select_set(True)
	bpy.context.view_layer.objects.active = obj
	bpy.ops.export_scene.gltf(
		filepath=str(OUTPUT_PATH),
		use_selection=True,
		export_format='GLB',
		export_apply=True,
		export_texcoords=True,
		export_normals=True,
		export_colors=True,
		export_yup=True,
	)


def main():
	ensure_dirs()
	reset_scene()

	body = build_body()
	head = build_head()
	neck = add_neck()

	character = join_meshes([body, neck, head], 'SphereheadCharacter')
	body_material = make_material('BodyMaterial', (0.18, 0.18, 0.2, 1.0), roughness=0.82)
	head_material = make_material('HeadMaterial', (0.82, 0.83, 0.78, 1.0), roughness=0.98)
	assign_materials(character, body_material, head_material)
	set_origin_to_feet(character)
	finalize_mesh(character)
	export_glb(character)


if __name__ == '__main__':
	main()
