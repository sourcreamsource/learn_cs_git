# 타입 힌트를 위해 Dict, Optional을 불러옴
from typing import Dict, Optional


# 브랜치 목록, HEAD 포인터, 현재 사용자(작성자) 상태를 관리하는 저장소 클래스임
class BranchRepository:
    """브랜치 이름표, HEAD, 현재 작성자와 초기화 여부를 함께 보관한다.

    브랜치 사전은 이름에서 최신 커밋 해시로 연결한다.
    HEAD는 현재 브랜치 이름이며 커밋 객체 자체를 보관하지 않는다.
    아직 커밋이 없는 브랜치의 값은 None이다.
    """
    # 브랜치 및 저장소 상태를 초기 상태로 비워두는 생성자 함수임
    def __init__(self) -> None:
        # 브랜치 이름과 최신 커밋 해시를 매핑하는 딕셔너리임 (예: {"main": "a1b2c3"})
        self._branches: Dict[str, Optional[str]] = {}
        # 현재 활성화된 브랜치 이름을 가리키는 HEAD 포인터임 (예: "main")
        self._head: Optional[str] = None
        # 현재 저장소를 사용하는 사용자(작성자) 이름임 (예: "Alice")
        self._author: Optional[str] = None
        # 저장소가 INIT 명령을 통해 초기화되었는지를 나타내는 플래그임
        self._is_initialized: bool = False

    # 저장소를 초기화하고 기본 main 브랜치 및 사용자를 설정하는 함수임
    def initialize(self, author: str) -> None:
        # 모든 브랜치 데이터를 비움
        """브랜치를 비우고 main, HEAD, 작성자를 다시 설정한다.

        입력 author는 상위 서비스에서 검사한 사용자 이름이다.
        main의 커밋은 None, HEAD는 main, 초기화 여부는 True가 된다.
        커밋과 색인을 비우는 일은 GitService가 별도로 수행한다.
        반환값은 None이다.
        """
        self._branches.clear()
        # 기본 브랜치인 main을 생성하고 아직 커밋이 없으므로 None으로 둠
        self._branches["main"] = None
        # HEAD를 main 브랜치로 설정함
        self._head = "main"
        # 현재 사용자 이름을 등록함
        self._author = author
        # 초기화 완료 상태로 플래그를 True로 변경함
        self._is_initialized = True

    # 저장소가 이미 초기화되었는지 여부를 확인하는 함수임
    def is_initialized(self) -> bool:
        # 초기화 플래그 값을 반환함
        return self._is_initialized

    # 현재 설정된 사용자 이름을 반환하는 함수임
    def get_author(self) -> Optional[str]:
        # 작성자 이름을 반환함
        return self._author

    # 현재 설정된 사용자 이름을 변경하는 함수임
    def set_author(self, author: str) -> None:
        # 작성자 이름을 새 이름으로 갱신함
        self._author = author

    # 현재 HEAD가 가리키고 있는 활성 브랜치 이름을 반환하는 함수임
    def get_head(self) -> Optional[str]:
        # HEAD 브랜치 이름을 반환함
        return self._head

    # HEAD 포인터를 다른 브랜치로 전환하는 함수임
    def set_head(self, branch_name: str) -> bool:
        # 전환하려는 브랜치가 존재하는지 검사함
        """존재하는 브랜치로 HEAD만 옮기고 성공 여부를 반환한다.

        없는 이름이면 False이며 상태를 바꾸지 않는다.
        성공하면 True다. 커밋을 복사하거나 브랜치의 최신 해시를 바꾸지 않는다.
        """
        if branch_name not in self._branches:
            # 브랜치가 없으면 실패(False)를 반환함
            return False
        # HEAD를 해당 브랜치로 변경함
        self._head = branch_name
        # 성공(True)을 반환함
        return True

    # 현재 활성화된 HEAD 브랜치가 가리키는 최신 커밋 해시를 반환하는 함수임
    def get_head_commit_hash(self) -> Optional[str]:
        # HEAD가 설정되어 있지 않으면 None을 반환함
        if not self._head:
            # 처리 결과를 호출한 곳에 돌려주고 이 함수의 실행을 끝냄.
            return None
        # 현재 브랜치에 매핑된 최신 커밋 해시를 반환함
        return self._branches.get(self._head)

    # 새로운 브랜치를 생성하는 함수임
    def create_branch(
        # 다음 단계에서 쓸 값을 계산하거나 꺼내 변수에 보관함.
        self, branch_name: str, commit_hash: Optional[str] = None
    # 앞에서 여러 줄로 적은 값이나 설정의 묶음을 마무리함.
    ) -> bool:
        # 이미 동일한 이름의 브랜치가 존재하는지 검사함
        if branch_name in self._branches:
            # 이미 있으면 실패(False)를 반환함
            return False
        # 새 브랜치를 등록하고 지정된 커밋 해시를 가리키게 함
        self._branches[branch_name] = commit_hash
        # 성공(True)을 반환함
        return True

    # 특정 브랜치가 가리키는 최신 커밋 해시를 갱신하는 함수임
    def update_branch(self, branch_name: str, commit_hash: str) -> bool:
        # 해당 브랜치가 존재하는지 확인함
        if branch_name not in self._branches:
            # 존재하지 않으면 실패(False)를 반환함
            return False
        # 브랜치의 포인터를 새 커밋 해시로 갱신함
        self._branches[branch_name] = commit_hash
        # 성공(True)을 반환함
        return True

    # 특정 이름의 브랜치가 저장소에 존재하는지 검사하는 함수임
    def branch_exists(self, branch_name: str) -> bool:
        # 브랜치 맵에 키가 존재하는지 여부를 반환함
        return branch_name in self._branches

    # 등록된 모든 브랜치와 그 커밋 해시의 복사본 딕셔너리를 반환하는 함수임
    def get_all_branches(self) -> Dict[str, Optional[str]]:
        # 딕셔너리의 복사본을 만들어 반환함
        return dict(self._branches)

    # 특정 브랜치가 가리키는 커밋 해시를 반환하는 함수임
    def get_branch_commit(self, branch_name: str) -> Optional[str]:
        # 해당 브랜치의 커밋 해시를 찾아 반환함
        return self._branches.get(branch_name)
