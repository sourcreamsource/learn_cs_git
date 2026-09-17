from bonus.benchmark import SortBenchmark  # 두 정렬의 시간 측정을 담당함.
from bonus.diff import SimpleDiff  # 파일의 줄 단위 비교를 담당함.
from constants.git_constants import DEFAULT_AUTHOR  # 기본 작성자 이름을 재사용함.
from constants.messages import ERROR_NOT_INITIALIZED  # 초기화 오류 문구를 재사용함.
from index.inverted_index import InvertedIndex  # 병합 기록도 등록할 검색 색인임.
from models.commit import Commit  # 병합 결과의 자료형임.
from repositories.branch_repository import BranchRepository  # 병합할 두 브랜치의 HEAD를 확인함.
from repositories.commit_repository import CommitRepository  # 병합 커밋을 저장함.
from services.commit_writer import CommitWriter  # 일반 커밋과 저장 절차를 공유함.
from utils.hash_generator import HashGenerator  # 같은 세션의 번호 생성기임.
from validators.file_validator import FileValidator  # 파일 읽기 전 경로 안전성을 검사함.


# 병합 조건·파일 비교 요청·성능 측정 요청을 조율하는 선택 과제 서비스임.
class BonusService:
    def __init__(  # 기본 서비스와 같은 부품을 전달받음.
        self,  # 생성하는 보너스 서비스임.
        commit_repo: CommitRepository,  # 공통 커밋 저장소임.
        branch_repo: BranchRepository,  # 공통 브랜치 저장소임.
        inverted_index: InvertedIndex,  # 공통 검색 색인임.
        hash_generator: HashGenerator | None = None,  # 공통 번호 발급기를 전달할 수 있음.
    ) -> None:  # 병합과 일반 커밋이 같은 정보를 쓰도록 연결함.
        self._commit_repo = commit_repo  # 병합 기록을 보관할 저장소임.
        self._branch_repo = branch_repo  # 현재·대상 브랜치를 확인할 저장소임.
        self._index = inverted_index  # 병합 기록을 검색할 색인임.
        if hash_generator is None:  # 전달된 생성기가 없을 때만 기본값을 만듦.
            hash_generator = HashGenerator()  # 독립 서비스 사용을 위한 기본 생성기임.
        self._hasher = hash_generator  # 사용하는 번호 생성기를 기억함.
        self._writer = CommitWriter(commit_repo, branch_repo, inverted_index, hash_generator)  # 같은 저장 절차를 연결함.

    def merge_branch(self, target_branch: str) -> tuple[bool, Commit | None, str]:  # 두 가지의 HEAD로 병합 커밋을 만듦.
        if not self._branch_repo.is_initialized():  # 병합 전에 저장소가 있어야 함.
            return False, None, ERROR_NOT_INITIALIZED  # 먼저 INIT이 필요함을 알림.
        target = target_branch.strip()  # 대상 이름의 양끝 공백을 정리함.
        if not self._branch_repo.branch_exists(target):  # 대상 브랜치가 존재해야 함.
            return False, None, f"Unknown branch: {target}"  # 알 수 없는 이름을 알려 줌.
        current = self._branch_repo.get_head()  # 병합 결과를 저장할 현재 브랜치임.
        if not current:  # 활성 브랜치가 없는 상태를 거부함.
            return False, None, "No active branch"  # 저장할 가지가 없다고 알림.
        if current == target:  # 자기 자신을 병합하는 것은 허용하지 않음.
            return False, None, "Cannot merge branch into itself"  # 대상 선택 오류를 알림.
        current_hash = self._branch_repo.get_head_commit_hash()  # 현재 가지의 마지막 기록임.
        target_hash = self._branch_repo.get_branch_commit(target)  # 대상 가지의 마지막 기록임.
        if not current_hash or not target_hash:  # 양쪽 모두 최소 한 커밋이 있어야 함.
            return False, None, "Both branches must have at least one commit"  # 빈 브랜치 병합은 거부함.
        parents = [current_hash, target_hash]  # 현재·대상 HEAD 순서로 부모 두 개를 지정함.
        author = self._branch_repo.get_author() or DEFAULT_AUTHOR  # 병합을 만든 사용자를 기록함.
        message = f"Merge branch '{target}' into {current}"  # 기존 병합 메시지 형식을 유지함.
        commit = self._writer.create(current, message, author, parents)  # 커밋·브랜치·색인을 함께 갱신함.
        return True, commit, f"Merged branch {target}"  # 병합 결과를 반환함.

    def diff_files(self, file1_path: str, file2_path: str) -> tuple[bool, str, str]:  # 안전 검사 후 텍스트를 비교함.
        first_sensitive = FileValidator.is_sensitive_path(file1_path)  # 첫 파일의 입력명과 실제 이름을 확인함.
        second_sensitive = FileValidator.is_sensitive_path(file2_path)  # 두 번째 파일도 읽기 전에 검사함.
        if first_sensitive or second_sensitive:  # 어느 한쪽이라도 민감 이름이면 중단함.
            return False, "", "Security error: sensitive file cannot be read"  # 파일 내용을 읽지 않고 거부함.
        try:  # 실제 파일 읽기에서 생길 수 있는 오류를 처리함.
            difference = SimpleDiff.diff_files(file1_path, file2_path)  # 줄 단위 비교 도구를 실행함.
            return True, difference, "Diff computed successfully"  # 비교 결과를 반환함.
        except FileNotFoundError:  # 입력한 파일이 없는 경우임.
            return False, "", "File not found"  # 전체 경로를 노출하지 않는 오류를 반환함.
        except Exception:  # 읽기 권한이나 인코딩 등 다른 실패를 처리함.
            return False, "", "Error reading files"  # 내부 정보 없이 실패를 알려 줌.

    def run_benchmark(self) -> str:  # 정해 둔 네 크기로 두 정렬을 측정함.
        results = SortBenchmark.run_benchmark([100, 500, 1000, 3000])  # 같은 입력으로 두 알고리즘을 실행함.
        return SortBenchmark.format_table(results)  # 화면에 출력할 비교표를 반환함.
