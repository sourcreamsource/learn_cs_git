from graph.traversal import GraphTraversal  # 그래프 알고리즘의 공통 호출 창구임.
from models.commit import Commit  # 조회 결과의 커밋 자료형임.
from repositories.branch_repository import BranchRepository  # 로그에 붙일 브랜치 이름을 조회함.
from repositories.commit_repository import CommitRepository  # 조회할 모든 커밋을 가져옴.


# 저장소 자료를 그래프 알고리즘에 전달하고 조회 오류를 정리함.
class GraphService:
    def __init__(self, commit_repo: CommitRepository, branch_repo: BranchRepository) -> None:  # 필요한 저장소를 받음.
        self._commit_repo = commit_repo  # 탐색할 커밋이 있는 보관함임.
        self._branch_repo = branch_repo  # 커밋을 가리키는 이름표 보관함임.

    def _get_commits_dict(self) -> dict[str, Commit]:  # 알고리즘에 넘길 해시별 지도를 구성함.
        commits = {}  # 커밋 번호로 부모를 바로 찾을 수 있는 사전임.
        for commit in self._commit_repo.find_all():  # 현재 저장된 기록을 하나씩 읽음.
            commits[commit.hash] = commit  # 번호와 실제 커밋을 연결함.
        return commits  # 알고리즘이 사용할 지도를 반환함.

    def get_topological_log(self) -> list[tuple[Commit, list[str]]]:  # 부모 우선 로그에 브랜치 이름을 붙임.
        commits = GraphTraversal.topological_sort(self._get_commits_dict())  # 부모가 먼저인 순서를 구함.
        labels = {}  # 커밋 번호별로 표시할 브랜치 이름들을 모음.
        for branch, commit_hash in self._branch_repo.get_all_branches().items():  # 각 브랜치의 최신 번호를 읽음.
            if commit_hash:  # 아직 커밋이 없는 브랜치는 표시할 곳이 없음.
                if commit_hash not in labels:  # 이 번호의 이름표 목록이 없으면 만듦.
                    labels[commit_hash] = []  # 여러 가지가 같은 커밋을 가리킬 수도 있음.
                labels[commit_hash].append(branch)  # 해당 커밋에 브랜치 이름을 붙임.
        result = []  # 화면이 사용할 커밋·이름표 쌍의 목록임.
        for commit in commits:  # 위상 정렬 순서를 그대로 유지함.
            result.append((commit, labels.get(commit.hash, [])))  # 이름표가 없으면 빈 목록을 사용함.
        return result  # 출력 형식 결정은 CLI에 맡김.

    # 커밋 번호의 존재를 확인한 뒤 선택한 방향의 최단 경로를 요청함.
    def get_shortest_path(self, commit1: str, commit2: str, directed: bool = False) -> tuple[bool, list[str] | None, str]:
        commits = self._get_commits_dict()  # 현재 그래프를 준비함.
        if commit1 not in commits:  # 시작 번호 자체가 존재하는지 확인함.
            return False, None, f"Unknown commit: {commit1}"  # 연결 없음과 구분되는 오류임.
        if commit2 not in commits:  # 도착 번호 자체도 확인함.
            return False, None, f"Unknown commit: {commit2}"  # 없는 커밋을 알려 줌.
        path = GraphTraversal.bfs_shortest_path(commits, commit1, commit2, directed=directed)  # 선택한 방향으로 탐색함.
        if path is None:  # 번호는 맞지만 서로 연결되지 않은 경우임.
            return True, None, "No path"  # 정상 조회의 빈 경로 결과임.
        return True, path, "Path found"  # 발견한 경로를 반환함.

    def get_ancestors(self, commit_hash: str) -> tuple[bool, list[str] | None, str]:  # 대상 커밋의 모든 조상을 찾음.
        commits = self._get_commits_dict()  # 현재 부모 관계를 준비함.
        if commit_hash not in commits:  # 대상 번호를 먼저 확인함.
            return False, None, f"Unknown commit: {commit_hash}"  # 없는 커밋을 알려 줌.
        ancestors = GraphTraversal.get_ancestors(commits, commit_hash)  # 부모 방향으로 모든 조상을 찾음.
        return True, ancestors, "Ancestors found"  # 발견 순서의 목록을 반환함.
