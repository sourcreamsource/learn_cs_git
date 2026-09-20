# 타입 힌트를 위해 Dict, List, Optional을 불러옴
from typing import Dict, List, Optional

# Commit 엔티티 모델 클래스를 불러옴
from models.commit import Commit


# 커밋 노드들을 해시맵(딕셔너리)에 저장하고 O(1) 속도로 조회하는 저장소 클래스임
class CommitRepository:
    # 커밋 해시맵 저장소를 초기화하는 생성자 함수임
    def __init__(self) -> None:
        # 커밋 해시 문자열을 키로 하고 Commit 객체를 값으로 갖는 해시맵임 (평가항목 2, 3: O(1) 조회 보장)
        self._commits: Dict[str, Commit] = {} # 🔥🔥🔥🔥🔥
        # [ self._commits 저장소의 실제 데이터 생김새 예시 ]
        # Key는 커밋 고유 해시(문자열), Value는 커밋의 상세 정보가 담긴 Commit 객체임.
        #
        # self._commits = {
        #     "a1b2c3": Commit(
        #         hash="a1b2c3",
        #         message="저장소 초기화 및 첫 파일 작성",
        #         author="Alice",
        #         timestamp="2026-09-21 10:00:00",
        #         parents=[]                         # 루트(최초) 커밋: 부모 없음
        #     ),
        #     "d4e5f6": Commit(
        #         hash="d4e5f6",
        #         message="로그인 화면 버튼 추가",
        #         author="Alice",
        #         timestamp="2026-09-21 10:05:00",
        #         parents=["a1b2c3"]                 # 일반 커밋: 직전 부모 커밋 해시 1개
        #     ),
        #     "g7h8i9": Commit(
        #         hash="g7h8i9",
        #         message="feature-login 브랜치 병합",
        #         author="Alice",
        #         timestamp="2026-09-21 10:10:00",
        #         parents=["d4e5f6", "x1y2z3"]       # 병합(Merge) 커밋: 부모 커밋 해시 2개
        #     )
        # }
        #
        # 💡 왜 리스트([])가 아닌 딕셔너리({})로 저장하는가?
        #    1. O(1) 초고속 조회: self._commits["a1b2c3"] 처럼 해시만 알면 10만 개 커밋이 있어도 즉시 찾아냄.
        #    2. 고유성 보장: 딕셔너리의 Key는 중복될 수 없으므로 같은 해시의 중복 저장을 방지함.



    # 새로운 커밋 노드를 저장소에 등록하는 함수임
    def save(self, commit: Commit) -> None:
        
        # 같은 해시로 기존 역사를 덮어쓰지 못하게 함.
        if commit.hash in self._commits:
            # 이미 쓰고 있는 번호라고 알림.
            raise ValueError(f"Duplicate commit: {commit.hash}")
        
        # 새 기록은 이미 존재하는 기록만 부모로 가질 수 있음.
        for parent_hash in commit.parents:
            # 없는 부모나 자기 자신을 부모로 지정하면 거부함.
            if parent_hash not in self._commits:
                # 이 규칙으로 정상 저장 과정에서 순환이 생기는 것을 막음.
                raise ValueError(f"Unknown commit: {parent_hash}")
        
        # 커밋의 고유 해시를 키로 하여 커밋 객체를 해시맵에 저장함
        self._commits[commit.hash] = commit

    # 커밋 해시로 특정 커밋 노드를 O(1) 시간복잡도로 단건 조회하는 함수임
    def find_by_hash(self, commit_hash: str) -> Optional[Commit]:
        # 해시맵에서 해당 해시의 커밋을 찾아 반환하며, 없으면 None을 반환함
        return self._commits.get(commit_hash)

    # 저장소에 등록된 모든 커밋 객체들의 리스트를 반환하는 함수임
    def find_all(self) -> List[Commit]:
        # 해시맵의 모든 값들을 리스트 형태로 변환하여 반환함
        return list(self._commits.values())

    # 특정 해시를 가진 커밋이 저장소에 이미 존재하는지 확인하는 함수임
    def exists(self, commit_hash: str) -> bool:
        # 딕셔너리의 in 키워드를 사용해 해시의 존재 여부를 불리언 값으로 반환함
        return commit_hash in self._commits

    # 저장된 전체 커밋 개수를 반환하는 함수임
    def count(self) -> int:
        # 해시맵에 저장된 항목의 총 개수를 반환함
        return len(self._commits)

    # 저장소의 모든 커밋 데이터를 비우는 초기화 함수임
    def clear(self) -> None:
        # 딕셔너리의 모든 요소를 삭제함
        self._commits.clear()
