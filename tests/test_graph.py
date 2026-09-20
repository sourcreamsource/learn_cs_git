# 시스템 파일 및 디렉토리 조작을 위해 os 모듈을 불러옴
import os
# 파이썬 시스템 런타임 모듈을 불러옴
import sys

# 프로젝트 내 git-app 디렉토리를 파이썬 모듈 검색 경로에 최우선 등록함
_git_app_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "git-app"
)
if _git_app_dir not in sys.path:
    sys.path.insert(0, _git_app_dir)

# 단위 테스트 프레임워크인 unittest 모듈을 불러옴
import unittest
# DAG 검증 클래스를 불러옴
from graph.dag import DAGValidator
# 그래프 탐색 알고리즘 클래스를 불러옴
from graph.traversal import GraphTraversal
# Commit 모델 클래스를 불러옴
from models.commit import Commit


# 커밋의 작성자 이름을 정렬 우선순위로 돌려주는 테스트용 함수임
def get_commit_author(commit: Commit) -> str:
    # 전달받은 커밋의 작성자 이름을 반환함
    return commit.author


# 그래프 알고리즘(위상 정렬, BFS 최단 경로, 조상 탐색, DAG 검증)을 검증하는 테스트 클래스임
class TestGraphAlgorithms(unittest.TestCase):
    # 테스트용 커밋 그래프를 준비하는 함수임
    def setUp(self):
        # c1 -> c2 -> c3 구조
        # c1 -> c4 -> c5 구조 (분기)
        # c3, c5 -> c6 (병합)
        self.commits = {
            "c1": Commit("c1", "Initial", "Alice", parents=[]),
            "c2": Commit("c2", "Branch A1", "Alice", parents=["c1"]),
            "c3": Commit("c3", "Branch A2", "Bob", parents=["c2"]),
            "c4": Commit("c4", "Branch B1", "Charlie", parents=["c1"]),
            "c5": Commit("c5", "Branch B2", "David", parents=["c4"]),
            "c6": Commit("c6", "Merge", "Alice", parents=["c3", "c5"]),
        }

    # 위상 정렬에서 부모가 항상 자식보다 먼저 나오는지 검증하는 테스트임 (평가항목 1, 3)
    def test_topological_sort(self):
        sorted_list = GraphTraversal.topological_sort(self.commits)
        self.assertEqual(len(sorted_list), 6)

        # 각 커밋의 인덱스를 기록하여 부모 인덱스가 자식보다 작은지 검증
        # 커밋 해시별 출력 위치를 담을 빈 딕셔너리임
        idx_map = {}
        # 정렬된 커밋을 하나씩 보며 해시와 위치를 연결함
        for index, commit in enumerate(sorted_list):
            # 해시로 출력 위치를 바로 찾을 수 있게 저장함
            idx_map[commit.hash] = index
        for commit in sorted_list:
            for p in commit.parents:
                self.assertLess(
                    idx_map[p],
                    idx_map[commit.hash],
                    f"Parent {p} must come before child {commit.hash}",
                )

    # 무방향 BFS 최단 경로 탐색 및 사전순 타이브레이킹 검증 테스트임 (평가항목 1, 3)
    def test_bfs_shortest_path_undirected(self):
        # c2에서 c4로 가는 최단 경로: c2 -> c1 -> c4 (길이 2)
        path = GraphTraversal.bfs_shortest_path(self.commits, "c2", "c4")
        self.assertIsNotNone(path)
        self.assertEqual(path, ["c2", "c1", "c4"])

        # c1에서 c6으로 가는 경로: c1 -> c2 -> c3 -> c6 또는 c1 -> c4 -> c5 -> c6 (둘 다 길이 3)
        # "c1->c2->c3->c6" vs "c1->c4->c5->c6" 중 사전순으로 c2가 c4보다 앞서므로 c2 경로 선택되어야 함!
        path_merge = GraphTraversal.bfs_shortest_path(self.commits, "c1", "c6")
        self.assertEqual(path_merge, ["c1", "c2", "c3", "c6"])

    # 단방향 BFS 최단 경로 검증 테스트임 (평가항목 4: 단방향 시 결과 차이)
    def test_bfs_shortest_path_directed(self):
        # 자식(c3)에서 조상(c1) 방향으로는 단방향 연결이 존재하므로 경로 발견됨
        path_up = GraphTraversal.bfs_shortest_path(
            self.commits, "c3", "c1", directed=True
        )
        self.assertIsNotNone(path_up)
        self.assertEqual(path_up, ["c3", "c2", "c1"])

        # 다른 가지의 c2에서 c4로는 부모 방향만으로는 갈 수 없으므로 None(No path)이 되어야 함!
        path_cross = GraphTraversal.bfs_shortest_path(
            self.commits, "c2", "c4", directed=True
        )
        self.assertIsNone(path_cross)

    # 모든 조상 커밋 탐색 검증 테스트임 (평가항목 1)
    def test_get_ancestors(self):
        ancestors_c6 = GraphTraversal.get_ancestors(self.commits, "c6")
        # c6의 모든 조상은 c1, c2, c3, c4, c5 총 5개여야 함
        self.assertEqual(len(ancestors_c6), 5)
        self.assertIn("c1", ancestors_c6)
        self.assertIn("c2", ancestors_c6)
        self.assertIn("c3", ancestors_c6)
        self.assertIn("c4", ancestors_c6)
        self.assertIn("c5", ancestors_c6)
        # 부모를 먼저, 그 부모의 부모를 나중에 찾는 일정한 BFS 발견 순서여야 함
        self.assertEqual(ancestors_c6, ["c3", "c5", "c2", "c4", "c1"])

        # 루트 커밋 c1은 조상이 0개여야 함
        ancestors_c1 = GraphTraversal.get_ancestors(self.commits, "c1")
        self.assertEqual(len(ancestors_c1), 0)

    # DAG 검증 및 사이클 감지 테스트임 (평가항목 3)
    def test_dag_cycle_detection(self):
        self.assertTrue(DAGValidator.validate(self.commits))

        # 사이클 발생 커밋 추가 (c1이 c6을 부모로 가리키게 하여 순환 생성)
        cyclic_commits = dict(self.commits)
        cyclic_commits["c1"] = Commit("c1", "Cycle", "Alice", parents=["c6"])
        self.assertTrue(DAGValidator.has_cycle(cyclic_commits))
        self.assertFalse(DAGValidator.validate(cyclic_commits))

    # 부모-자식 관계를 유지하며 author 순으로 정렬하는 고급 위상 정렬 검증 (평가항목 4)
    def test_topological_sort_with_priority(self):
        result = GraphTraversal.topological_sort_with_priority(
            self.commits, priority_key_func=get_commit_author
        )
        self.assertEqual(len(result), 6)
        # 커밋 해시별 출력 위치를 담을 빈 딕셔너리임
        idx_map = {}
        # 정렬된 커밋을 하나씩 보며 해시와 위치를 연결함
        for index, commit in enumerate(result):
            # 해시로 출력 위치를 바로 찾을 수 있게 저장함
            idx_map[commit.hash] = index
        for commit in result:
            for p in commit.parents:
                self.assertLess(idx_map[p], idx_map[commit.hash])


if __name__ == "__main__":
    unittest.main()
