def snake_to_camel(snake_str: str) -> str:
    """snake_case 를 CamelCase로 변환한다.
    """
    cleaned_str = ''.join(char if char.isalnum() else '_' for char in snake_str).strip('_')
    words = filter(None, cleaned_str.split('_'))
    return ''.join(word.capitalize() for word in words)


assert (snake_to_camel("quick_bake") == "QuickBake")
assert (snake_to_camel("__quick_bake") == "QuickBake")
assert (snake_to_camel("__quick_bake__") == "QuickBake")
assert (snake_to_camel("__quick_-bake__") == "QuickBake")


def float_to_symbol(value: float) -> str:
    """소수점 숫자를 파일명에 들어가기 좋게 단위를 올리고 소수점을 제거한다.
    """
    return str(int(value * 100))


assert (float_to_symbol(0.3) == "30")
assert (float_to_symbol(0.15) == "15")
assert (float_to_symbol(1.25) == "125")
assert (float_to_symbol(10.24) == "1024")
assert (float_to_symbol(1) == "100")
assert (float_to_symbol(64) == "6400")
assert (float_to_symbol(1024) == "102400")
assert (float_to_symbol(1024.512) == "102451")


def get_image_size_symbol(w: int, h: int) -> str:
    if w == h and ((w & (w - 1)) == 0):
        return f"{w // 1024}K" if w >= 1024 else str(w)
    elif ((w & (w - 1)) == 0) and ((h & (h - 1)) == 0):
        return f"{w // 1024}x{h // 1024}K" if w >= 1024 and h >= 1024 else f"{w}x{h}"
    return f"{w}x{h}"


assert (get_image_size_symbol(256, 256) == "256")
assert (get_image_size_symbol(512, 512) == "512")
assert (get_image_size_symbol(1024, 1024) == "1K")
assert (get_image_size_symbol(2048, 2048) == "2K")
assert (get_image_size_symbol(4096, 4096) == "4K")
assert (get_image_size_symbol(8192, 8192) == "8K")
assert (get_image_size_symbol(4096, 2048) == "4x2K")


def baketype_to_symbol(baketype: str) -> str:
    """Baketype 이름을 짧게 줄여준다.
    대응되지 않는 이름은 입력받은 그대로 리턴한다.
    """
    symbols = {
        "Normal": "N",
        "AmbientOcclusion": "AO",
        "ZDepth": "Z"
    }
    return symbols.get(baketype, baketype)


assert (baketype_to_symbol("Normal") == "N")
assert (baketype_to_symbol("AmbientOcclusion") == "AO")
assert (baketype_to_symbol("ZDepth") == "Z")
assert (baketype_to_symbol("BaseColor") == "BaseColor")  # 특별히 지정된 경우를 제외하고는 입력 그대로 리턴
