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

# 임시 파일을 다루기 위해 tempfile 모듈을 불러옴
import tempfile
# 단위 테스트 프레임워크인 unittest 모듈을 불러옴
import unittest
# 역색인 클래스를 불러옴
from index.inverted_index import InvertedIndex
# 브랜치 저장소 클래스를 불러옴
from repositories.branch_repository import BranchRepository
# 커밋 저장소 클래스를 불러옴
from repositories.commit_repository import CommitRepository
# 보너스 서비스 클래스를 불러옴
from services.bonus_service import BonusService
# Git 서비스 클래스를 불러옴
from services.git_service import GitService
# 그래프 서비스 클래스를 불러옴
from services.graph_service import GraphService
# 검색 서비스 클래스를 불러옴
from services.search_service import SearchService
# 카운터 기반 해시 전략 클래스를 불러옴
from utils.hash_generator import CounterHashStrategy, HashGenerator


# 서비스 계층의 비즈니스 유스케이스 및 오케스트레이션을 종합 검증하는 테스트 클래스임
class TestServices(unittest.TestCase):
    # 테스트 전 의존성 객체들을 조립함
    def setUp(self):
        self.commit_repo = CommitRepository()
        self.branch_repo = BranchRepository()
        self.inverted_index = InvertedIndex()
        # 테스트 재현성을 위해 카운터 해시 전략 사용 (c000001, c000002...)
        self.hasher = HashGenerator(CounterHashStrategy(prefix="c"))

        self.git_service = GitService(
            self.commit_repo,
            self.branch_repo,
            self.inverted_index,
            self.hasher,
        )
        self.graph_service = GraphService(self.commit_repo, self.branch_repo)
        self.search_service = SearchService(
            self.commit_repo, self.inverted_index
        )
        self.bonus_service = BonusService(
            self.commit_repo,
            self.branch_repo,
            self.inverted_index,
            self.hasher,
        )

    # 초기화, 커밋, 브랜치, 스위치 전체 흐름 검증 테스트임 (평가항목 1)
    def test_git_workflow(self):
        # 1. 초기화
        init_res = self.git_service.init_repository("Alice")
        self.assertEqual(init_res["branch"], "main")
        self.assertEqual(init_res["author"], "Alice")

        # 2. 첫 번째 커밋
        ok, c1, br = self.git_service.create_commit("Initial commit")
        self.assertTrue(ok)
        self.assertEqual(c1.hash, "c000001")
        self.assertEqual(c1.parents, [])

        # 3. 브랜치 생성 및 전환
        ok_b, _ = self.git_service.create_branch("feature")
        self.assertTrue(ok_b)
        ok_s, _ = self.git_service.switch_branch("feature")
        self.assertTrue(ok_s)
        self.assertEqual(self.git_service.get_current_branch(), "feature")

        # 4. 피처 브랜치에서 커밋
        ok, c2, _ = self.git_service.create_commit("Add login feature")
        self.assertTrue(ok)
        self.assertEqual(c2.parents, ["c000001"])

        # 5. 역색인 검색 검증
        search_res = self.search_service.search_by_keyword("login")
        self.assertEqual(len(search_res), 1)
        self.assertEqual(search_res[0].hash, c2.hash)

        # 6. 위상 정렬 로그 검증
        logs = self.graph_service.get_topological_log()
        self.assertEqual(len(logs), 2)
        # 부모인 c1이 항상 자식인 c2보다 먼저 나와야 함
        self.assertEqual(logs[0][0].hash, c1.hash)
        self.assertEqual(logs[1][0].hash, c2.hash)

        # 7. 최단 경로 탐색 검증
        ok_p, path, _ = self.graph_service.get_shortest_path(c1.hash, c2.hash)
        self.assertTrue(ok_p)
        self.assertEqual(path, [c1.hash, c2.hash])

        # 8. 조상 탐색 검증
        ok_a, anc, _ = self.graph_service.get_ancestors(c2.hash)
        self.assertTrue(ok_a)
        self.assertEqual(anc, [c1.hash])

    # 보너스 브랜치 병합(Merge) 및 파일 Diff 검증 테스트임
    def test_merge_and_diff(self):
        # 저장소 초기화 및 기본 커밋 생성
        self.git_service.init_repository("Alice")
        self.git_service.create_commit("Base commit")

        # feature 브랜치 생성 및 이동
        self.git_service.create_branch("feature")
        self.git_service.switch_branch("feature")
        self.git_service.create_commit("Feature work")

        # main 브랜치로 복귀하여 다른 커밋 생성
        self.git_service.switch_branch("main")
        self.git_service.create_commit("Main work")

        # main 브랜치에서 feature 브랜치를 병합함
        ok_m, m_commit, _ = self.bonus_service.merge_branch("feature")
        self.assertTrue(ok_m)
        self.assertIsNotNone(m_commit)
        # 머지 커밋의 부모는 2개여야 함
        self.assertEqual(len(m_commit.parents), 2)

        # 파일 Diff 테스트
        with tempfile.NamedTemporaryFile(
            "w+", dir=os.path.dirname(__file__)
        ) as f1, tempfile.NamedTemporaryFile("w+", dir=os.path.dirname(__file__)) as f2:
            f1.write("Hello\nWorld\n")
            f1.flush()
            f2.write("Hello\nPython\n")
            f2.flush()

            ok_d, diff_text, _ = self.bonus_service.diff_files(
                f1.name, f2.name
            )
            self.assertTrue(ok_d)
            self.assertIn("+ Python", diff_text)
            self.assertIn("- World", diff_text)

        # 환경 변수 파일은 실제로 읽기 전에 보안 오류로 차단되어야 함
        ok_secret, _, secret_message = self.bonus_service.diff_files(
            ".env", "ordinary.txt"
        )
        # 민감 파일 비교는 실패해야 함
        self.assertFalse(ok_secret)
        # 보안 차단 문구가 반환되어야 함
        self.assertIn("Security error", secret_message)


if __name__ == "__main__":
    unittest.main()
