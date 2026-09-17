from constants.git_constants import DEFAULT_PROMPT_AUTHOR  # INIT 질문의 기본 사용자 이름을 불러옴.


# 이미 받은 인자는 유지하고 빠진 값만 질문하는 대화형 입력 도구임.
class InteractiveHandler:
    @staticmethod  # 질문 하나에는 별도 객체 상태가 필요하지 않음.
    def prompt_input(prompt_text: str, default: str = "") -> str:  # 질문·기본값·취소 처리를 한곳에 모음.
        display = f"? {prompt_text}: "  # 기본값 없는 질문 문구를 만듦.
        if default:  # 기본값이 있으면 사용자가 볼 수 있게 표시함.
            display = f"? {prompt_text} [{default}]: "  # 기본값을 대괄호에 넣음.
        try:  # 입력 도중 취소도 정상 흐름으로 다룸.
            answer = input(display).strip()  # 답변 양끝의 공백을 정리함.
            if not answer and default:  # 답 없이 엔터를 누르면 기본값을 사용함.
                return default  # 준비된 기본값을 반환함.
            return answer  # 직접 입력한 답을 반환함.
        except (EOFError, KeyboardInterrupt):  # 입력 종료 또는 Ctrl+C를 받았는지 확인함.
            return ""  # 명령 담당자가 빈 입력으로 처리하도록 함.

    @classmethod  # 공통 질문 함수에서 같은 클래스의 prompt_input을 사용함.
    def _ask_one(cls, args: list[str], title: str, prompt: str, default: str = "") -> str | None:  # 값 하나를 받음.
        if args:  # 이미 명령에 값이 들어 있으면 다시 묻지 않음.
            return args[0]  # 파서가 보존한 공백·따옴표를 그대로 전달함.
        print(f"[대화형 입력 모드: {title}]")  # 어떤 작업의 질문인지 알려 줌.
        answer = cls.prompt_input(prompt, default)  # 한 번의 질문으로 값을 받음.
        if answer:  # 사용자가 값을 입력했는지 확인함.
            return answer  # 받은 값을 명령 담당자에게 전달함.
        return None  # 입력 취소 또는 빈 답변을 표시함.

    @classmethod  # 두 값 질문에도 같은 입력 함수를 재사용함.
    def _ask_pair(cls, args: list[str], title: str, first_prompt: str, second_prompt: str) -> tuple[str | None, str | None]:
        first = None  # 아직 첫 번째 인자를 받지 않은 상태임.
        second = None  # 아직 두 번째 인자를 받지 않은 상태임.
        if len(args) > 0:  # 첫 번째 값이 이미 있으면 보존함.
            first = args[0]  # 시작 번호 또는 첫 파일 경로임.
        if len(args) > 1:  # 두 번째 값도 이미 있으면 보존함.
            second = args[1]  # 도착 번호 또는 두 번째 파일 경로임.
        if not first:  # 첫 값이 빠진 경우에만 질문함.
            print(f"[대화형 입력 모드: {title}]")  # 진행할 작업 이름을 보여 줌.
            first = cls.prompt_input(first_prompt)  # 첫 번째 값을 질문함.
        if not second:  # 두 번째 값이 빠진 경우에만 질문함.
            second = cls.prompt_input(second_prompt)  # 두 번째 값을 질문함.
        return first, second  # 받았거나 취소된 두 값을 그대로 전달함.

    @classmethod  # 기존 명령별 호출 이름을 유지함.
    def ask_init(cls, existing_args: list[str]) -> str | None:  # 저장소 작성자를 질문함.
        return cls._ask_one(existing_args, "저장소 초기화", "사용자 이름(Author)을 입력하세요", DEFAULT_PROMPT_AUTHOR)  # 기본 이름도 전달함.

    @classmethod  # 브랜치 생성 질문의 이름을 유지함.
    def ask_branch(cls, existing_args: list[str]) -> str | None:  # 새 브랜치 이름을 질문함.
        return cls._ask_one(existing_args, "브랜치 생성", "새로 생성할 브랜치 이름을 입력하세요")  # 생성용 질문 문구임.

    @classmethod  # 브랜치 전환 질문의 이름을 유지함.
    def ask_switch(cls, existing_args: list[str]) -> str | None:  # 이동할 브랜치를 질문함.
        return cls._ask_one(existing_args, "브랜치 전환", "이동할 브랜치 이름을 입력하세요")  # 전환용 질문 문구임.

    @classmethod  # 커밋 질문의 이름을 유지함.
    def ask_commit(cls, existing_args: list[str]) -> str | None:  # 새 커밋 메시지를 질문함.
        return cls._ask_one(existing_args, "커밋 생성", "커밋 메시지를 입력하세요")  # 메시지 질문 문구임.

    @classmethod  # 경로 질문의 이름을 유지함.
    def ask_path(cls, existing_args: list[str]) -> tuple[str | None, str | None]:  # 출발·도착 번호를 질문함.
        return cls._ask_pair(existing_args, "최단 경로 탐색", "시작 커밋 해시(commit1)를 입력하세요", "도착 커밋 해시(commit2)를 입력하세요")  # 경로용 두 질문임.

    @classmethod  # 조상 질문의 이름을 유지함.
    def ask_ancestors(cls, existing_args: list[str]) -> str | None:  # 조상을 찾을 번호를 질문함.
        return cls._ask_one(existing_args, "조상 커밋 탐색", "조상을 찾을 커밋 해시를 입력하세요")  # 조상 조회 질문임.

    @classmethod  # 검색 질문의 이름을 유지함.
    def ask_search(cls, existing_args: list[str]) -> str | None:  # 검색할 단어를 질문함.
        return cls._ask_one(existing_args, "키워드 검색", "검색할 키워드를 입력하세요")  # 단어 검색 질문임.

    @classmethod  # 병합 질문의 이름을 유지함.
    def ask_merge(cls, existing_args: list[str]) -> str | None:  # 병합할 가지 이름을 질문함.
        return cls._ask_one(existing_args, "브랜치 병합", "병합해 올 대상 브랜치 이름을 입력하세요")  # 대상 브랜치 질문임.

    @classmethod  # 파일 비교 질문의 이름을 유지함.
    def ask_diff(cls, existing_args: list[str]) -> tuple[str | None, str | None]:  # 파일 경로 두 개를 질문함.
        return cls._ask_pair(existing_args, "파일 Diff 비교", "비교할 첫 번째 파일 경로를 입력하세요", "비교할 두 번째 파일 경로를 입력하세요")  # 파일 비교용 두 질문임.
