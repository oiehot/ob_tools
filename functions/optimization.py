import bpy

AVAILABLE_TYPES: list[str] = ["MESH", "META", "LIGHT"]


def get_best_data_name(obj) -> str:
    """Object이름에 가장 적합한 Mesh의 이름을 리턴한다.

    Chair => ChairMesh
    Chair.001 => ChairMesh (메시의 사용자가 여러명인 경우)
    Chair.001 => ChairMesh.001 (메시의 사용자가 1명인 경우)

    SpotLight => SpotLightData
    SpotLight.001 => SpotLightData.001

    MetaBall => MetaBallData
    MetaBall.001 => MetaBallData.001
    """
    if obj.type not in AVAILABLE_TYPES:
        raise Exception("메시만 사용 가능")

    obj_type: str = str(obj.type)
    data_type: str | None = None
    match obj_type:
        case "MESH":
            data_type = obj_type.capitalize()
        case _:
            data_type = "Data"

    data = obj.data
    # old_mesh_name: str = mesh.name
    tokens: list = obj.name.split(".")
    name: str = tokens[0]
    object_count: int = 0
    object_count_str: str | None = None
    mesh_user_count: int = data.users
    new_name: str | None = None

    if len(tokens) >= 2:
        object_count = int(tokens[1])
        object_count_str = f"{object_count:03}"  # 3 => "003"

    if object_count == 0:
        new_name = f"{name}{data_type}"

    elif object_count > 0 and mesh_user_count > 1:
        new_name = f"{name}{data_type}"

    else:
        new_name = f"{name}{data_type}.{object_count_str}"

    return new_name


def fix_data_names() -> None:
    for obj in bpy.data.objects:
        if obj.type in AVAILABLE_TYPES:
            data = obj.data
            obj_name: str = obj.name
            old_data_name: str = data.name
            new_data_name: str = get_best_data_name(obj)
            if old_data_name != new_data_name:
                print(f"이름 변경: {obj_name}/{old_data_name} => {obj_name}/{new_data_name}")
                data.name = new_data_name
