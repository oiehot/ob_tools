import math
import logging

import bpy
from bpy.types import GeometryNodeTree, Collection
from mathutils import Vector, Euler

from ob_tools.utils.log_utils import setup_logger
from ob_tools.functions.context import select_objects, deselect_all
from ob_tools.functions.collection import (
    create_collection,
    get_all_collections,
    get_all_layer_collections,
    get_layer_collection,
    set_active_layer_collection,
    get_collection_bound_box,
)


TARGET_COLLECTION_NAME:str = "_TargetCollection"
SNOW_COLLECTION_NAME:str = "_SnowCollection"
SNOW_PLANE_NAME:str = "_SnowPlane"
MARGIN:float = 0.1
_log = setup_logger("Snow", logging.DEBUG)


def link_gn(filepath:str, geometry_node_name:str) -> GeometryNodeTree:
    """특정 블렌더 파일에서 Geometry Node를 링크합니다.
    """
    with bpy.data.libraries.load(filepath, link=True) as (data_from, data_to):
        data_to.node_groups = [name for name in data_from.node_groups if name == geometry_node_name]

    if len(data_to.node_groups) <= 0:
        raise Exception(f"Geometry Node {geometry_node_name} cannot be found")

    if len(data_to.node_groups) >= 2:
        raise Exception(f"There are two or more Geometry Nodes named {geometry_node_name}")

    gn: GeometryNodeTree = data_to.node_groups[0]
    assert(gn.name == geometry_node_name)
    assert(type(gn) == bpy.types.GeometryNodeTree)
    return gn


def make_snow(input_blender_path:str, geometry_node_name: str, input_fbx_path: str, output_fbx_path:str, density:float, voxel_size:float, decimate:bool, decimate_ratio:float):
    _log.info(f"BlenderPythonModuleVersion: {bpy.app.version}")
    _log.info(f"InputBlenderPath: {input_blender_path}")
    _log.info(f"InputFbxPath: {input_fbx_path}")
    _log.info(f"OutputFbxPath: {output_fbx_path}")
    _log.info(f"Density: {density}")
    _log.info(f"VoxelSize: {voxel_size}")
    _log.info(f"TargetCollectionName: {TARGET_COLLECTION_NAME}")
    _log.info(f"SnowCollectionName: {SNOW_COLLECTION_NAME}")
    _log.info(f"BoundingBoxMargin: {MARGIN}")

    _log.info(f"Reset Scene")
    bpy.ops.wm.read_homefile()

    _log.info(f"Link GeometryNode {geometry_node_name} from {input_blender_path}")
    gn_snow = link_gn(input_blender_path, geometry_node_name)

    _log.info(f"Create a TargetCollection ({TARGET_COLLECTION_NAME})")
    target_collection: Collection = create_collection(TARGET_COLLECTION_NAME)

    _log.info(f"Active a TargetLayerCollection ({TARGET_COLLECTION_NAME})")
    set_active_layer_collection(TARGET_COLLECTION_NAME)

    _log.info(f"Import FBX ({input_fbx_path})")
    result = bpy.ops.import_scene.fbx(filepath=input_fbx_path)
    assert("FINISHED" in result)

    _log.info(f"Target Objects:")
    for obj in target_collection.objects:
        _log.info(f"\t* {obj.name} (Object)")

    _log.info(f"Create a SnowCollection ({SNOW_COLLECTION_NAME})")
    snow_collection: Collection = create_collection(SNOW_COLLECTION_NAME)
    snow_layer_collection: LayerCollection = get_layer_collection(SNOW_COLLECTION_NAME)

    _log.info(f"Active a SnowLayerCollection ({SNOW_COLLECTION_NAME})")
    set_active_layer_collection(SNOW_COLLECTION_NAME)

    _log.info(f"Get TargetCollection BoundingBox ({TARGET_COLLECTION_NAME})")
    min_coord, max_coord = get_collection_bound_box(TARGET_COLLECTION_NAME)
    min_coord -= Vector((MARGIN, MARGIN, MARGIN))
    max_coord += Vector((MARGIN, MARGIN, MARGIN))
    bounding_box_size = max_coord - min_coord

    _log.info(f"Create a SnowEmitterPlane")
    plane_location = (min_coord + max_coord) / 2
    plane_location.z = max_coord.z
    plane_result = bpy.ops.mesh.primitive_plane_add(
        size=1.0,
        location=plane_location,
        rotation=Euler((0,math.radians(180),0)), # Normal을 아래 방향으로 회전시켜야 눈이 위에서 아래로 떨어짐.
        scale=Vector((1,1,1))
    )
    assert("FINISHED" in plane_result)
    plane = bpy.context.active_object
    plane.name = SNOW_PLANE_NAME
    plane.data.name = SNOW_PLANE_NAME + "Data"
    plane.dimensions = Vector((bounding_box_size.x, bounding_box_size.y, 1))
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    _log.info(f"Apply {geometry_node_name} Modifier to SnowEmitterPlane")
    snow_modifier = plane.modifiers.new(name=f"{geometry_node_name}_Modifier", type="NODES")

    _log.info(f"Set {geometry_node_name} Input Values")
    snow_modifier.node_group = gn_snow  # bpy.data.node_groups[geometry_node]
    modifier_items = snow_modifier.node_group.interface.items_tree
    density_id = modifier_items["Density"].identifier
    voxel_size_id = modifier_items["Voxel Size"].identifier
    target_collection_id = modifier_items["Target Collection"].identifier
    snow_modifier[density_id] = density
    snow_modifier[voxel_size_id] = voxel_size
    snow_modifier[target_collection_id] = target_collection

    _log.info(f"Set Desnity to {snow_modifier[density_id]}")
    _log.info(f"Set VoxelSize to {snow_modifier[voxel_size_id]}")
    _log.info(f"Set TargetCollection to {snow_modifier[target_collection_id]}")

    if decimate:
        _log.info(f"Add Decimate Modifier to SnowEmitterPlane")
        _log.info(f"Decimate Ratio: {decimate_ratio}")
        decimate_modifier = plane.modifiers.new(name="DecimateModifier", type="DECIMATE")
        decimate_modifier.decimate_type = "COLLAPSE"
        decimate_modifier.ratio = decimate_ratio
        decimate_modifier.use_symmetry = False
        decimate_modifier.use_collapse_triangulate = False

    _log.info(f"Hide Unused LayerCollections")
    layer_collections = [lc for lc in get_all_layer_collections() if lc not in [snow_layer_collection]]
    for lc in layer_collections:
        lc.hide_viewport = True
        lc.exclude = True

    # _log.info(f"Save Output Blend File")
    # bpy.ops.wm.save_as_mainfile(filepath="d:/tmp/output.blend")

    _log.info(f"Apply Snow Modifier")
    bpy.ops.object.modifier_apply(modifier=snow_modifier.name)
    if decimate:
        _log.info(f"Apply Decimate Modifier")
        bpy.ops.object.modifier_apply(modifier=decimate_modifier.name)

    _log.info(f"Select Final Objects")
    deselect_all()
    select_objects(snow_collection.objects)

    _log.info(f"Export FBX")
    bpy.ops.export_scene.fbx(
        filepath=output_fbx_path,
        use_selection=True,
        axis_forward="-Z", axis_up="Y", apply_unit_scale=True,
        global_scale=1.0
    )
