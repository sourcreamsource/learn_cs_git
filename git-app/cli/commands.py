from cli.bonus_commands import BonusCommands  # 선택 과제 명령 담당자를 불러옴.
from cli.history_commands import HistoryCommands  # 기록 조회 명령 담당자를 불러옴.
from cli.repository_commands import RepositoryCommands  # 저장소 변경 명령 담당자를 불러옴.
from constants.help_text import HELP_TEXT  # 도움말 문구는 상수 파일에서 읽음.
from constants.messages import ERROR_NOT_INITIALIZED  # 초기화 전 조회의 공통 오류임.
from services.bonus_service import BonusService  # 조립 시 받을 서비스의 자료형임.
from services.git_service import GitService  # 저장소 상태를 확인할 서비스임.
from services.graph_service import GraphService  # 그래프 조회 서비스의 자료형임.
from services.search_service import SearchService  # 검색 서비스의 자료형임.
from validators.command_validator import validate_command_shape  # 모든 명령에 같은 입력 검사를 적용함.


# 명령별 허용 문법을 검사한 뒤 알맞은 담당자에게 넘기는 연결 창구임.
class CommandDispatcher:
    def __init__(  # 화면에 필요한 서비스들을 전달받음.
        self,  # 이번에 만드는 명령 연결 객체임.
        git_service: GitService,  # 저장소 변경과 초기화 상태를 담당함.
        graph_service: GraphService,  # 부모 관계 탐색을 담당함.
        search_service: SearchService,  # 검색과 정렬을 담당함.
        bonus_service: BonusService,  # 병합·파일 비교·성능 측정을 담당함.
    ) -> None:  # 담당자들과 명령 연결표를 구성함.
        self._git = git_service  # 초기화 여부 확인과 기존 검사 코드에서 사용하는 참조임.
        self._graph = graph_service  # 앱에 연결된 그래프 서비스를 기억함.
        self._search = search_service  # 앱에 연결된 검색 서비스를 기억함.
        self._bonus = bonus_service  # 앱에 연결된 보너스 서비스를 기억함.
        repository = RepositoryCommands(git_service)  # 저장소 변경 담당자를 만듦.
        history = HistoryCommands(graph_service, search_service)  # 기록 조회 담당자를 만듦.
        bonus = BonusCommands(git_service, bonus_service)  # 선택 과제 담당자를 만듦.
        self._commands = {  # 값의 순서는 (처리 함수, 최대 인자 수, 허용 옵션, 질문 전 초기화 검사)임.
            "INIT": (repository.handle_init, 1, (), False),  # 이름 하나를 받아 초기화함.
            "BRANCH": (repository.handle_branch, 1, (), False),  # 이름을 받은 뒤 서비스가 상태를 검사함.
            "SWITCH": (repository.handle_switch, 1, (), False),  # 이름을 받은 뒤 브랜치를 전환함.
            "COMMIT": (repository.handle_commit, 1, (), False),  # 메시지 하나를 받아 저장함.
            "LOG": (history.handle_log, 0, ("sort-by",), True),  # 초기화된 저장소에서 로그를 조회함.
            "PATH": (history.handle_path, 2, ("directed",), True),  # 커밋 번호 두 개로 경로를 조회함.
            "ANCESTORS": (history.handle_ancestors, 1, (), True),  # 번호 하나로 조상을 조회함.
            "SEARCH": (history.handle_search, 1, ("author",), True),  # 단어 또는 작성자로 검색함.
            "MERGE": (bonus.handle_merge, 1, (), False),  # 대상 이름을 받은 뒤 서비스가 병합 조건을 검사함.
            "DIFF": (bonus.handle_diff, 2, (), False),  # 저장소 초기화 없이도 텍스트 파일을 비교함.
            "BENCH": (bonus.handle_bench, 0, (), False),  # 인자 없이 정렬 시간을 측정함.
            "HELP": (self.handle_help, 0, (), False),  # 인자 없이 도움말을 출력함.
        }  # 명령별 차이는 이 연결표 한곳에서 확인할 수 있음.

    def dispatch(self, action: str, args: list[str], options: dict[str, str]) -> None:  # 공통 검사 후 명령을 전달함.
        rule = self._commands.get(action)  # 명령 이름에 연결된 처리 규칙을 찾음.
        if rule is None:  # 등록되지 않은 명령이면 실행할 수 없음.
            print(f"Unknown command: {action}. 'HELP'를 입력하여 사용법을 확인하세요.")  # 기존 오류 문구를 유지함.
            return  # 알 수 없는 명령 처리를 마침.
        handler, maximum, allowed, check_initialized = rule  # 각 설정에 쉬운 이름을 붙임.
        error = validate_command_shape(args, options, maximum, allowed)  # 인자 수와 옵션을 먼저 검사함.
        if error is not None:  # 문법이 틀렸으면 질문하거나 저장하지 않음.
            print(error)  # 공통 검증기가 만든 오류를 출력함.
            return  # 잘못된 명령을 중단함.
        if check_initialized and not self._git.is_initialized():  # 조회 전에 필요한 저장소 상태를 확인함.
            print(ERROR_NOT_INITIALIZED)  # 먼저 INIT을 실행해야 함을 알려 줌.
            return  # 조회 담당자에게 넘기지 않음.
        handler(args, options)  # 검사가 끝난 명령을 담당자에게 넘김.

    def handle_help(self, args: list[str], options: dict[str, str]) -> None:  # 검사를 통과한 HELP의 출력만 담당함.
        print(HELP_TEXT)  # 별도 파일의 도움말을 그대로 출력함.
