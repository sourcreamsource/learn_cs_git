from cli.interactive import InteractiveHandler  # 생략된 인자를 질문하는 도구임.
from cli.presenter import show_created_commit  # 커밋 생성 결과의 공통 출력 함수임.
from services.git_service import GitService  # 저장소·브랜치·커밋 기능을 실행함.


# INIT·BRANCH·SWITCH·COMMIT처럼 저장소를 변경하는 명령을 담당함.
class RepositoryCommands:
    def __init__(self, git_service: GitService) -> None:  # 저장소 변경에 필요한 서비스만 받음.
        self._git = git_service  # 다른 명령에서도 같은 저장소를 사용함.

    def handle_init(self, args: list[str], options: dict[str, str]) -> None:  # 작성자 이름을 받아 초기화함.
        author = InteractiveHandler.ask_init(args)  # 이름을 받았으면 쓰고 없으면 질문함.
        if not author:  # 이름 입력을 취소했거나 빈 이름을 입력한 경우임.
            print("Invalid args: author name is required")  # 필요한 값을 알려 줌.
            return  # 저장소는 변경하지 않음.
        try:  # 서비스의 이름 검증 실패를 화면에서 처리함.
            result = self._git.init_repository(author)  # 검증 후 저장소를 초기화함.
        except ValueError as error:  # 공백뿐인 이름처럼 잘못된 입력을 처리함.
            print(str(error))  # 서비스가 만든 입력 오류만 출력함.
            return  # 초기화 성공 문구를 출력하지 않음.
        print("Initialized repository.")  # 초기화 성공을 알림.
        print(f"Current branch: {result['branch']}")  # 새 기본 브랜치를 보여 줌.
        print(f"Current user: {result['author']}")  # 현재 작성자를 보여 줌.

    def handle_branch(self, args: list[str], options: dict[str, str]) -> None:  # 새 브랜치를 만듦.
        branch = InteractiveHandler.ask_branch(args)  # 새 브랜치 이름을 받음.
        if not branch:  # 사용자가 이름 입력을 취소했는지 확인함.
            print("Invalid args: branch name is required")  # 브랜치 이름이 필요함을 알림.
            return  # 생성은 실행하지 않음.
        success, message = self._git.create_branch(branch)  # 서비스가 이름과 중복 여부를 검사함.
        print(message)  # 성공 또는 실패 이유를 그대로 출력함.

    def handle_switch(self, args: list[str], options: dict[str, str]) -> None:  # 현재 브랜치를 바꿈.
        branch = InteractiveHandler.ask_switch(args)  # 이동할 브랜치 이름을 받음.
        if not branch:  # 이름 입력이 없는지 확인함.
            print("Invalid args: branch name is required")  # 필요한 값을 알려 줌.
            return  # 현재 브랜치를 유지함.
        success, message = self._git.switch_branch(branch)  # 서비스가 브랜치 존재를 검사하고 이동함.
        print(message)  # 이동 결과를 출력함.

    def handle_commit(self, args: list[str], options: dict[str, str]) -> None:  # 일반 커밋을 만듦.
        message = InteractiveHandler.ask_commit(args)  # 커밋 설명을 받음.
        if not message:  # 메시지 입력이 취소되었는지 확인함.
            print("Invalid args: commit message is required")  # 메시지가 필요함을 알림.
            return  # 커밋은 생성하지 않음.
        success, commit, branch_or_error = self._git.create_commit(message)  # 서비스에 저장을 요청함.
        if success and commit is not None:  # 정상적으로 새 커밋을 받은 경우임.
            show_created_commit(branch_or_error, commit)  # 브랜치와 새 번호를 출력함.
        else:  # 입력이나 저장소 상태가 잘못된 경우임.
            print(branch_or_error)  # 서비스의 오류 문구를 출력함.
