from typing import Optional  # 오류가 없을 때 None을 반환함을 표시함.


# 인자 개수와 옵션 이름을 검사하며 화면 출력이나 데이터 변경은 하지 않음.
def validate_command_shape(args: list[str], options: dict[str, str], maximum: int, allowed: tuple[str, ...]) -> Optional[str]:
    if len(args) > maximum:  # 이 명령이 받을 수 있는 인자 수를 넘었는지 확인함.
        return "Invalid args: too many arguments"  # 실행 전에 입력 오류를 반환함.
    for name in options:  # 사용자가 지정한 옵션 이름을 하나씩 확인함.
        if name not in allowed:  # 이 명령이 지원하지 않는 옵션을 찾음.
            return f"Invalid args: unsupported option --{name}"  # 잘못된 옵션 이름을 알려 줌.
    return None  # 인자와 옵션의 모양이 올바르다는 뜻임.
