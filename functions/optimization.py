import bpy


def get_best_data_name(obj) -> str:
    """Object와 연결된 Data에게 가장 적합한 이름을 리턴한다.

    Chair => Chair_Mesh
    Chair.001 => Chair.001_Mesh
    SpotLight => SpotLight_Data
    SpotLight.001 => SpotLight.001_Data
    FrontHair.L => FrontHair.L_Curve
    FrontHair.001.L => FrontHair.001.L_Curve
    FrontHair.001.L.Strands => FrontHair.001.L.Strands_Curve
    MetaBall => MetaBall_Data
    MetaBall.001 => MetaBall.001_Data
    """

    obj_type_str: str = str(obj.type)
    data_type_str: str | None = None

    match obj_type_str:
        case "MESH" | "CURVE":
            data_type_str = obj_type_str.capitalize()
        case _:
            data_type_str = "Data"

    data = obj.data
    new_name: str | None = f"{obj.name}_{data_type_str}"
    return new_name


def fix_data_names() -> None:
    for obj in bpy.data.objects:
        data = obj.data
        # 데이터 블록(data)이 Linked 데이터 블록인 경우 continue 한다.
        if data.library:
            continue
        old_data_name: str = data.name
        new_data_name: str = get_best_data_name(obj)
        if old_data_name != new_data_name:
            print(f"Fix Data Name: {obj.name} > {old_data_name} => {obj.name} > {new_data_name}")
            data.name = new_data_name
