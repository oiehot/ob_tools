from json import JSONEncoder


class ObjectVertexGroupEncoder(JSONEncoder):
    """블렌더 Mesh Object를 받아 VertexGroup 정보가 담긴 Dictionary 데이터를 리턴한다.
    json 덤프시 사용된다.
    """

    def default(self, obj):
        result = {
            "object_name": obj.name,
            "object_type": obj.type,
            "data_name": obj.data.name
        }

        if obj.type != "MESH":
            return result
        result["vertex_groups"] = []

        for vertex_group in obj.vertex_groups:
            vg_dict: dict = {
                "name": vertex_group.name,
                "data": None
            }
            vg_data: list = []
            for vertex in obj.data.vertices:
                try:
                    i = vertex.index
                    weight = vertex_group.weight(i)
                    vg_data.append({
                        "index": i,
                        "weight": weight
                    })
                except RuntimeError:
                    continue
            vg_dict["data"] = vg_data
            result["vertex_groups"].append(vg_dict)
        return result
