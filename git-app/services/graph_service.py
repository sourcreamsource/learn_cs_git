from graph.traversal import GraphTraversal  # 그래프 알고리즘의 공통 호출 창구임.

from models.commit import Commit  # 조회 결과의 커밋 자료형임.

from repositories.branch_repository import BranchRepository  # 로그에 붙일 브랜치 이름을 조회함.

from repositories.commit_repository import CommitRepository  # 조회할 모든 커밋을 가져옴.


# 저장소 자료를 그래프 알고리즘에 전달하고 조회 오류를 정리함.
class GraphService:
    """저장소의 커밋을 그래프 함수에 전달하고 조회 결과를 정리한다.

    알고리즘은 GraphTraversal, 데이터 보관은 저장소,
    화면 출력은 명령 화면에 맡긴다. LOG·PATH·ANCESTORS의 연결 담당이다.
    """
                    # 이미 default로 이미 다 들어가서 class 가져다 쓸 때 인자 전달이 필요없다.
    def __init__(self, commit_repo: CommitRepository, branch_repo: BranchRepository) -> None:  # 필요한 저장소를 받음.
        self._commit_repo = commit_repo  # 탐색할 커밋이 있는 보관함임.
        self._branch_repo = branch_repo  # 커밋을 가리키는 이름표 보관함임.

    # ✅ 
    # 그래프 알고리즘에 넘길 해시별 지도를 구성
    def _get_commits_dict(self) -> dict[str, Commit]:  
        """전체 커밋을 해시로 조회할 수 있는 새 사전을 만든다.

        매 호출마다 커밋 N개를 읽어 시간·추가 공간 O(N)이 든다.
        사전만 새로 만들며 안의 Commit 객체는 공유하는 얕은 복사다.
        따라서 커밋 객체 자체의 외부 변경까지 막는 복사는 아니다.
        """
        commits = {}  # 커밋 번호로 부모를 바로 찾을 수 있는 사전임.
        
        for commit in self._commit_repo.find_all():  # 현재 저장된 기록을 하나씩 읽음.
            commits[commit.hash] = commit  # 번호와 실제 커밋을 연결함.
        
        return commits  # 알고리즘이 사용할 지도를 반환함.
        # ⚫️ [ _get_commits_dict() 반환값(return) 실제 생김새 예시 ]
        # 커밋 해시(문자열)를 키(Key)로 하고, Commit 객체를 값(Value)으로 갖는 딕셔너리(사전)임.
        #
        # {
        #     "a1b2c3": Commit(
        #         hash="a1b2c3",
        #         message="초기 저장소 설정",
        #         author="Alice",
        #         timestamp="2026-09-21 10:00:00",
        #         parents=[]                         # 최초 커밋이므로 부모 없음 (root)
        #     ),
        #     "d4e5f6": Commit(
        #         hash="d4e5f6",
        #         message="로그인 기능 구현",
        #         author="Alice",
        #         timestamp="2026-09-21 10:05:00",
        #         parents=["a1b2c3"]                 # 직전 부모 커밋 해시 1개
        #     ),
        #     "g7h8i9": Commit(
        #         hash="g7h8i9",
        #         message="feature 브랜치 병합",
        #         author="Alice",
        #         timestamp="2026-09-21 10:10:00",
        #         parents=["d4e5f6", "x1y2z3"]       # 병합 커밋(Merge)이므로 부모 2개
        #     )
        # }
        #
        # 💡 왜 이렇게 만드나요?
        #    위상 정렬(Topological Sort)이나 최단 경로(BFS) 알고리즘이 동작할 때,
        #    commits["d4e5f6"].parents 처럼 커밋 해시만으로 부모/자식 연결 정보를
        #    O(1) 속도로 즉시 찾아내기 위한 '지도(Lookup Table)' 역할을 함.

        # ⚫️ CommitRepository에 이미 커밋 데이가 있는데, find_all로 가져와서 for문 돌리는 이유
        # 1. 캡슐화 (정보 은닉)
        # 2. 방어적 복사 (원본 데이터 보호)



    # ✅ 🔥🔥🔥🔥🔥 위상 정렬을 하는 메서드
    # _get_commits_dict 함수를 사용
    def get_topological_log(self) -> list[tuple[Commit, list[str]]]:            # 부모 우선 로그에 브랜치 이름을 붙임.
        
        """전체 커밋을 부모 우선으로 정렬하고 브랜치 이름표를 붙인다.

        반환값은 (Commit, 브랜치 이름 목록)의 목록이다.
        현재 브랜치의 조상만이 아니라 저장된 모든 커밋을 대상으로 한다.
        부모 누락이나 순환이 있으면 위상 정렬의 ValueError가 전달된다.
        """
        commits = GraphTraversal.topological_sort(self._get_commits_dict())     # 부모가 먼저인 순서를 구함.
        
        labels = {}  # 커밋 번호별로 표시할 브랜치 이름들을 모음.
        
        for branch, commit_hash in self._branch_repo.get_all_branches().items():  # 각 브랜치의 최신 번호를 읽음.
            if commit_hash:                             # 아직 커밋이 없는 브랜치는 표시할 곳이 없음.
                if commit_hash not in labels:           # 이 번호의 이름표 목록이 없으면 만듦.
                    labels[commit_hash] = []            # 여러 가지가 같은 커밋을 가리킬 수도 있음.
                labels[commit_hash].append(branch)      # 해당 커밋에 브랜치 이름을 붙임.
        
        result = []                                     # 화면이 사용할 커밋·이름표 쌍의 목록임.
        
        for commit in commits:                          # 위상 정렬 순서를 그대로 유지함.
            result.append((commit, labels.get(commit.hash, [])))  # 이름표가 없으면 빈 목록을 사용함.
        
        return result                                   # 출력 형식 결정은 CLI에 맡김.


    # ✅ 🔥🔥🔥🔥🔥
    # 커밋 번호의 존재를 확인한 뒤 선택한 방향의 최단 경로를 요청함.
    def get_shortest_path(self, commit1: str, commit2: str, directed: bool = False) -> tuple[bool, list[str] | None, str]:
        """해시 존재를 검사한 뒤 방향 설정에 맞는 최단 경로를 조회한다.

        반환값은 (성공 여부, 경로 또는 None, 문구)다.
        없는 해시는 (False, None, Unknown commit 문구),
        연결이 없으면 (True, None, No path)다.
        directed=False는 양방향, True는 자식에서 부모 방향이다.
        그래프 내부의 부모 누락으로 생긴 ValueError는 그대로 전달될 수 있다.
        """
        commits = self._get_commits_dict()  # 현재 그래프를 준비함.
        
        if commit1 not in commits:  # 시작 번호 자체가 존재하는지 확인함.
            return False, None, f"Unknown commit: {commit1}"  # 연결 없음과 구분되는 오류임.
        
        if commit2 not in commits:  # 도착 번호 자체도 확인함.
            return False, None, f"Unknown commit: {commit2}"  # 없는 커밋을 알려 줌.
        
        path = GraphTraversal.bfs_shortest_path(commits, commit1, commit2, directed=directed)  # 선택한 방향으로 탐색함.
        
        if path is None:  # 번호는 맞지만 서로 연결되지 않은 경우임.
            return True, None, "No path"  # 정상 조회의 빈 경로 결과임.
        
        return True, path, "Path found"  # 발견한 경로를 반환함.


    # ✅ 🔥🔥🔥🔥🔥
    def get_ancestors(self, commit_hash: str) -> tuple[bool, list[str] | None, str]:  # 대상 커밋의 모든 조상을 찾음.
        """대상 해시를 검사하고 모든 조상 목록을 반환한다.

        정상 결과는 (True, 조상 목록, Ancestors found)다.
        부모 없는 루트의 조상은 빈 목록이며 정상 결과다.
        없는 대상은 (False, None, Unknown commit 문구)로 구분한다.
        """
        commits = self._get_commits_dict()  # 현재 부모 관계를 준비함.
        
        if commit_hash not in commits:  # 대상 번호를 먼저 확인함.
            return False, None, f"Unknown commit: {commit_hash}"  # 없는 커밋을 알려 줌.
        
        ancestors = GraphTraversal.get_ancestors(commits, commit_hash)  # 부모 방향으로 모든 조상을 찾음.
        
        return True, ancestors, "Ancestors found"  # 발견 순서의 목록을 반환함.
