from index.inverted_index import InvertedIndex  # 커밋 생성 후 갱신할 검색 색인임.
from models.commit import Commit  # 저장할 커밋 카드의 자료형임.
from repositories.branch_repository import BranchRepository  # 최신 번호를 갱신할 브랜치 저장소임.
from repositories.commit_repository import CommitRepository  # 커밋을 보관하는 저장소임.
from utils.hash_generator import HashGenerator  # 중복 없는 새 번호를 발급함.


# COMMIT과 MERGE가 공유하는 저장 절차를 한곳에서 담당함.
class CommitWriter:
    """COMMIT과 MERGE가 공유하는 커밋 저장 절차를 담당한다.

    커밋 저장, 브랜치 최신 번호 변경, 역색인 등록을
    한곳에 모아 일반 기록과 병합 기록의 갱신 방식이 달라지지 않게 한다.
    """
    def __init__(  # 기록·브랜치·색인·번호 발급기를 받음.
        self,  # 생성되는 저장 담당 객체임.
        commit_repo: CommitRepository,  # 해시를 키로 커밋을 저장함.
        branch_repo: BranchRepository,  # 현재 브랜치의 최신 번호를 바꿈.
        inverted_index: InvertedIndex,  # 단어·작성자별 번호를 등록함.
        hash_generator: HashGenerator,  # 세션 발급 이력을 유지하는 생성기임.
    ) -> None:  # 필요한 도구를 내부에 보관함.
        self._commits = commit_repo  # 실제 커밋 저장소를 기억함.
        self._branches = branch_repo  # 실제 브랜치 저장소를 기억함.
        self._index = inverted_index  # 공유하는 색인을 기억함.
        self._hasher = hash_generator  # 번호 중복 검사를 맡길 생성기를 기억함.

    def create(self, branch: str, message: str, author: str, parents: list[str]) -> Commit:  # 결정된 정보로 새 커밋을 저장함.
        """중복 없는 번호로 커밋을 저장하고 브랜치와 두 색인을 갱신한다.

        입력은 브랜치 이름, 메시지, 작성자, 부모 해시 목록이다.
        부모 목록을 복사한 Commit을 만들고 저장 → 브랜치 변경 → 색인
        등록 순서로 처리한 뒤 그 Commit을 반환한다.
        없는 브랜치, 중복 해시, 없는 부모는 ValueError가 될 수 있다.
        성공 반환 전에 검색 색인도 갱신된다.
        중간 예외 때 앞선 변경을 되돌리는 트랜잭션 기능은 없다.
        """
        if not self._branches.branch_exists(branch):  # 잘못된 가지에 저장해 일부 자료만 바뀌는 것을 막음.
            raise ValueError(f"Unknown branch: {branch}")  # 저장 전에 잘못된 대상을 알려 줌.
        commit_hash = self._hasher.next_unique_hash(message, self._commits.exists)  # 같은 세션에서 새 번호를 발급함.
        commit = Commit(hash=commit_hash, message=message, author=author, parents=list(parents))  # 호출자의 부모 목록을 복사함.
        self._commits.save(commit)  # 1. 부모 존재와 중복을 검사하고 커밋을 저장함.
        self._branches.update_branch(branch, commit.hash)  # 2. 해당 브랜치의 최신 번호를 바꿈.
        self._index.add_commit(commit.hash, commit.message, commit.author)  # 3. 두 검색 색인에 즉시 등록함.
        return commit  # 세 단계가 끝난 새 커밋을 호출자에게 반환함.
