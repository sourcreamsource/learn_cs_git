import os  # 파일 이름과 심볼릭 링크의 실제 대상을 확인함.


# 보너스 DIFF에서 사용하며 파일 내용을 읽지 않고 경로만 검사함.
class FileValidator:
    @staticmethod  # 검사에 별도 객체 상태가 필요하지 않음.
    def has_sensitive_name(file_path: str) -> bool:  # 알려진 환경 파일·개인 키 이름인지 확인함.
        name = os.path.basename(file_path).lower()  # 마지막 파일 이름을 소문자로 정리함.
        if name in (".env", "id_rsa", "id_ed25519"):  # 대표 민감 파일 이름을 확인함.
            return True  # 내용을 읽기 전에 차단해야 함.
        if name.startswith(".env."):  # 환경 파일의 변형 이름도 확인함.
            return True  # 개발용·운영용 환경 파일도 차단함.
        return name.endswith((".pem", ".key"))  # 알려진 개인 키 확장자를 확인함.

    @classmethod  # 입력 경로와 실제 경로에 같은 이름 검사를 사용함.
    def is_sensitive_path(cls, file_path: str) -> bool:  # 링크를 이용한 이름 우회도 검사함.
        resolved = os.path.realpath(file_path)  # 파일을 열지 않고 링크의 실제 대상을 구함.
        for candidate in (file_path, resolved):  # 사용자가 준 이름과 실제 이름을 모두 확인함.
            if cls.has_sensitive_name(candidate):  # 둘 중 하나라도 민감 이름이면 차단함.
                return True  # 비교 서비스가 파일을 읽지 않도록 알림.
        return False  # 알려진 이름 규칙에 해당하지 않음. 내용의 비밀값 검사는 아님.
