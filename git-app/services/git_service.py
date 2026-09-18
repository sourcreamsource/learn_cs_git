from constants.git_constants import DEFAULT_AUTHOR, DEFAULT_BRANCH  # 초기 브랜치와 작성자 기본값임.
from constants.messages import ERROR_BRANCH_EXISTS, ERROR_NOT_INITIALIZED, ERROR_UNKNOWN_BRANCH  # 공통 오류 문구임.
from index.inverted_index import InvertedIndex  # 초기화할 검색 색인임.
from models.commit import Commit  # 생성 결과로 반환할 커밋 자료형임.
from repositories.branch_repository import BranchRepository  # 브랜치·HEAD·사용자를 보관함.
from repositories.commit_repository import CommitRepository  # 커밋을 보관함.
from services.commit_writer import CommitWriter  # 실제 커밋 저장 절차를 담당함.
from utils.hash_generator import HashGenerator  # 커밋 번호를 발급함.
from validators.input_validator import InputValidator  # 이름과 메시지의 내용을 검사함.


# 저장소 초기화·브랜치 전환·일반 커밋의 작업 규칙을 결정함.
class GitService:
    def __init__(  # 필요한 저장 도구들을 전달받음.
        self,  # 생성하는 저장소 서비스임.
        commit_repo: CommitRepository,  # 커밋 보관함임.
        branch_repo: BranchRepository,  # 브랜치 상태 보관함임.
        inverted_index: InvertedIndex,  # 검색 색인임.
        hash_generator: HashGenerator | None = None,  # 테스트에서는 번호 생성기를 바꿀 수 있음.
    ) -> None:  # 전달받은 도구를 연결함.
        self._commit_repo = commit_repo  # INIT 때 비울 커밋 저장소임.
        self._branch_repo = branch_repo  # 현재 브랜치와 작성자를 확인할 저장소임.
        self._index = inverted_index  # INIT 때 함께 비울 색인임.
        if hash_generator is None:  # 별도 생성기를 받지 않은 경우임.
            hash_generator = HashGenerator()  # 기본 번호 생성기를 준비함.
        self._hasher = hash_generator  # 이 세션에서 사용할 생성기를 기억함.
        self._writer = CommitWriter(commit_repo, branch_repo, inverted_index, hash_generator)  # 공통 저장 담당자를 연결함.

    def init_repository(self, author: str) -> dict[str, str]:  # 이름을 검사한 뒤 새 저장소 상태로 초기화함.
        valid, cleaned_author = InputValidator.validate_author(author)  # 공백 이름을 먼저 검사함.
        if not valid:  # 잘못된 입력은 기존 자료를 보존해야 함.
            raise ValueError(cleaned_author)  # 데이터 삭제 전에 입력 오류를 알림.
        self._commit_repo.clear()  # 이전 커밋 기록을 비움.
        self._index.clear()  # 이전 기록을 가리키는 검색 색인도 비움.
        self._branch_repo.initialize(cleaned_author)  # main·HEAD·작성자를 다시 설정함.
        return {"branch": DEFAULT_BRANCH, "author": cleaned_author}  # 화면에 알려 줄 초기화 결과임.

    def create_branch(self, branch_name: str) -> tuple[bool, str]:  # 현재 커밋을 가리키는 새 가지를 만듦.
        if not self.is_initialized():  # 아직 INIT을 실행하지 않았는지 확인함.
            return False, ERROR_NOT_INITIALIZED  # 초기화부터 필요하다고 알림.
        valid, name = InputValidator.validate_branch_name(branch_name)  # 빈 이름과 공백을 검사함.
        if not valid:  # 잘못된 브랜치 이름을 거부함.
            return False, name  # 검사기의 오류 문구를 반환함.
        if self._branch_repo.branch_exists(name):  # 같은 이름을 이미 쓰는지 확인함.
            return False, ERROR_BRANCH_EXISTS.format(name=name)  # 기존 가지를 덮어쓰지 않음.
        current = self._branch_repo.get_head_commit_hash()  # 현재 가지의 최신 커밋 번호임.
        self._branch_repo.create_branch(name, current)  # 커밋 복사 없이 번호만 가리키는 이름표를 만듦.
        return True, f"Created branch: {name}"  # 생성된 가지 이름을 알림.

    def switch_branch(self, branch_name: str) -> tuple[bool, str]:  # HEAD가 가리키는 브랜치를 바꿈.
        if not self.is_initialized():  # 브랜치를 사용하기 전에 초기화가 필요함.
            return False, ERROR_NOT_INITIALIZED  # 초기화 오류를 반환함.
        valid, name = InputValidator.validate_branch_name(branch_name)  # 이름의 모양을 검사함.
        if not valid:  # 빈 이름이나 공백을 거부함.
            return False, name  # 검사 오류를 그대로 반환함.
        if not self._branch_repo.branch_exists(name):  # 이동할 가지가 존재해야 함.
            return False, ERROR_UNKNOWN_BRANCH.format(name=name)  # 알 수 없는 브랜치라고 알림.
        self._branch_repo.set_head(name)  # 활성 브랜치의 이름을 바꿈.
        return True, f"Switched to branch: {name}"  # 이동 결과를 반환함.

    def create_commit(self, message: str) -> tuple[bool, Commit | None, str]:  # 일반 커밋의 작성자와 부모를 결정함.
        if not self.is_initialized():  # 저장소가 먼저 준비되어 있어야 함.
            return False, None, ERROR_NOT_INITIALIZED  # 초기화 오류를 반환함.
        valid, cleaned_message = InputValidator.validate_commit_message(message)  # 비어 있는 메시지를 검사함.
        if not valid:  # 잘못된 메시지로 기록하지 않음.
            return False, None, cleaned_message  # 메시지 검사 오류를 반환함.
        branch = self._branch_repo.get_head()  # 현재 선택된 브랜치 이름임.
        if not branch:  # 저장할 활성 브랜치가 있는지 확인함.
            return False, None, "No active branch"  # 저장할 곳이 없다고 알림.
        author = self._branch_repo.get_author() or DEFAULT_AUTHOR  # 현재 작성자를 가져옴.
        parent = self._branch_repo.get_head_commit_hash()  # 현재 가지의 이전 커밋을 찾음.
        parents = []  # 첫 커밋은 부모가 없는 상태로 만듦.
        if parent:  # 이전 기록이 있을 때만 부모 한 개를 지정함.
            parents.append(parent)  # 현재 HEAD의 커밋을 부모로 넣음.
        commit = self._writer.create(branch, cleaned_message, author, parents)  # 공통 저장 절차를 실행함.
        return True, commit, branch  # 새 커밋과 저장한 브랜치를 반환함.

    def list_branches(self) -> list[str]:  # 생성된 순서대로 브랜치 이름 목록을 조회함.
        return list(self._branch_repo.get_all_branches())  # 복사한 이름 목록만 반환하여 원본 상태를 보호함.

    def get_current_branch(self) -> str | None:  # 현재 선택된 가지를 조회함.
        return self._branch_repo.get_head()  # 브랜치 저장소의 HEAD 값을 반환함.

    def get_current_author(self) -> str | None:  # 현재 작성자를 조회함.
        return self._branch_repo.get_author()  # 브랜치 저장소의 작성자 값을 반환함.

    def is_initialized(self) -> bool:  # INIT 실행 여부를 조회함.
        return self._branch_repo.is_initialized()  # 상태 보관은 브랜치 저장소에 맡김.
