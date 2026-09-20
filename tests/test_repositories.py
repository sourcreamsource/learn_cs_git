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
# 테스트 대상인 Commit 모델 클래스를 불러옴
from models.commit import Commit
# 테스트 대상인 BranchRepository 클래스를 불러옴
from repositories.branch_repository import BranchRepository
# 테스트 대상인 CommitRepository 클래스를 불러옴
from repositories.commit_repository import CommitRepository


# 저장소 계층의 인메모리 CRUD 및 상태 관리를 검증하는 테스트 클래스임
class TestRepositories(unittest.TestCase):
    # 각 테스트 시작 전 호출되는 준비 함수임
    def setUp(self):
        self.commit_repo = CommitRepository()
        self.branch_repo = BranchRepository()

    # CommitRepository의 커밋 저장, 조회, 존재 검사 테스트임
    def test_commit_repository_crud(self):
        c1 = Commit(
            hash="c001", message="First", author="Alice", parents=[]
        )
        self.commit_repo.save(c1)

        # 해시로 단건 조회 검증
        found = self.commit_repo.find_by_hash("c001")
        self.assertIsNotNone(found)
        self.assertEqual(found.message, "First")

        # 존재 여부 검증
        self.assertTrue(self.commit_repo.exists("c001"))
        self.assertFalse(self.commit_repo.exists("unknown"))

        # 전체 개수 검증
        self.assertEqual(self.commit_repo.count(), 1)

    # BranchRepository의 초기화 및 브랜치 관리 테스트임
    def test_branch_repository_operations(self):
        self.assertFalse(self.branch_repo.is_initialized())
        self.branch_repo.initialize("Alice")
        self.assertTrue(self.branch_repo.is_initialized())
        self.assertEqual(self.branch_repo.get_author(), "Alice")
        self.assertEqual(self.branch_repo.get_head(), "main")

        # 새 브랜치 생성 및 전환 테스트
        self.assertTrue(self.branch_repo.create_branch("feature", "c001"))
        self.assertTrue(self.branch_repo.branch_exists("feature"))
        self.assertTrue(self.branch_repo.set_head("feature"))
        self.assertEqual(self.branch_repo.get_head(), "feature")
        self.assertEqual(self.branch_repo.get_head_commit_hash(), "c001")


# 단독 실행 시 테스트 실행
if __name__ == "__main__":
    unittest.main()
