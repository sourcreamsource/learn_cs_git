from cli.interactive import InteractiveHandler  # 부족한 보너스 명령 인자를 질문함.
from cli.presenter import show_created_commit  # 일반 커밋과 같은 생성 결과 형식을 사용함.
from services.bonus_service import BonusService  # 병합·비교·성능 측정을 요청함.
from services.git_service import GitService  # 현재 브랜치 이름을 조회함.


# 선택 과제 명령을 기본 저장소·조회 명령과 분리함.
class BonusCommands:
    def __init__(self, git_service: GitService, bonus_service: BonusService) -> None:  # 필요한 두 서비스를 받음.
        self._git = git_service  # 병합 결과에 표시할 현재 브랜치를 조회함.
        self._bonus = bonus_service  # 보너스 기능의 실제 작업을 맡김.

    def handle_merge(self, args: list[str], options: dict[str, str]) -> None:  # 대상 브랜치를 현재 브랜치에 병합함.
        target = InteractiveHandler.ask_merge(args)  # 대상 이름을 받음.
        if not target:  # 대상 입력이 취소되었는지 확인함.
            print("Invalid args: branch name to merge is required")  # 필요한 인자를 알려 줌.
            return  # 병합하지 않음.
        success, commit, message = self._bonus.merge_branch(target)  # 서비스에 두 부모 커밋 생성을 요청함.
        if success and commit is not None:  # 병합 커밋을 정상적으로 받은 경우임.
            show_created_commit(self._git.get_current_branch(), commit)  # 생성 결과를 공통 형식으로 출력함.
        else:  # 병합할 수 없는 조건이면 이유를 출력함.
            print(message)  # 자기 병합·빈 브랜치 등의 오류를 보여 줌.

    def handle_diff(self, args: list[str], options: dict[str, str]) -> None:  # 두 텍스트 파일을 비교함.
        first, second = InteractiveHandler.ask_diff(args)  # 파일 경로가 빠졌으면 질문함.
        if not first or not second:  # 경로 두 개가 모두 있는지 확인함.
            print("Invalid args: two file paths required (DIFF <file1> <file2>)")  # 필요한 입력을 알려 줌.
            return  # 파일을 읽지 않음.
        success, difference, message = self._bonus.diff_files(first, second)  # 검증 후 비교를 요청함.
        if success:  # 비교가 정상적으로 끝났는지 확인함.
            print(difference)  # 추가·삭제·공통 줄을 출력함.
        else:  # 파일 읽기나 보안 검사에 실패한 경우임.
            print(message)  # 경로나 내용을 노출하지 않는 오류를 출력함.

    def handle_bench(self, args: list[str], options: dict[str, str]) -> None:  # 두 정렬의 시간을 비교함.
        print("[정렬 알고리즘 성능 비교 벤치마크 실행 중...]")  # 측정이 시작되었음을 알려 줌.
        print(self._bonus.run_benchmark())  # 서비스가 만든 시간 비교표를 출력함.
