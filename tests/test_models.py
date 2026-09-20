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


# Commit 모델의 동작을 검증하는 테스트 클래스임
class TestCommitModel(unittest.TestCase):
    # 커밋 생성 및 기본 필드 값 검증 테스트임
    def test_commit_creation(self):
        # 커밋 객체 생성
        c = Commit(
            hash="a1b2c3",
            message="Initial commit",
            author="Alice",
            parents=[],
        )
        # 해시 필드 검증
        self.assertEqual(c.hash, "a1b2c3")
        # 메시지 필드 검증
        self.assertEqual(c.message, "Initial commit")
        # 작성자 필드 검증
        self.assertEqual(c.author, "Alice")
        # 부모 목록 필드 검증
        self.assertEqual(c.parents, [])
        # 타임스탬프 필드가 자동으로 채워졌는지 검증
        self.assertIsNotNone(c.timestamp)

    # 커밋 객체의 to_dict() 변환 검증 테스트임
    def test_commit_to_dict(self):
        c = Commit(
            hash="d4e5f6",
            message="Second commit",
            author="Bob",
            parents=["a1b2c3"],
        )
        d = c.to_dict()
        self.assertEqual(d["hash"], "d4e5f6")
        self.assertEqual(d["parents"], ["a1b2c3"])


# 단독 실행 시 테스트 실행
if __name__ == "__main__":
    unittest.main()
