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
# 테스트 대상인 InvertedIndex 클래스를 불러옴
from index.inverted_index import InvertedIndex


# 역색인(Inverted Index)의 토큰화 및 고속 검색 기능을 검증하는 테스트 클래스임
class TestInvertedIndex(unittest.TestCase):
    # 테스트 전 실행되는 설정 함수임
    def setUp(self):
        self.index = InvertedIndex()

    # 키워드 역색인 추가 및 검색 검증 테스트임
    def test_keyword_index(self):
        self.index.add_commit("h1", "Add login feature", "Alice")
        self.index.add_commit("h2", "Fix login bug", "Bob")
        self.index.add_commit("h3", "Update README documentation", "Alice")

        # "login" 검색 시 h1, h2가 모두 찾아지는지 검증
        results = self.index.search_by_keyword("login")
        self.assertEqual(len(results), 2)
        self.assertIn("h1", results)
        self.assertIn("h2", results)

        # 대소문자 무시 검색 검증
        results_caps = self.index.search_by_keyword("LOGIN")
        self.assertEqual(results_caps, results)

        # 공백 포함 검색어는 모든 단어를 가진 커밋만 찾아야 함
        phrase_results = self.index.search_by_keyword("login feature")
        self.assertEqual(phrase_results, ["h1"])

        # 일치하지 않는 키워드 검색 시 빈 리스트 반환 검증
        no_res = self.index.search_by_keyword("payment")
        self.assertEqual(no_res, [])

    # 작성자 역색인 추가 및 검색 검증 테스트임
    def test_author_index(self):
        self.index.add_commit("h1", "Commit 1", "Alice")
        self.index.add_commit("h2", "Commit 2", "Bob")
        self.index.add_commit("h3", "Commit 3", "Alice")

        # Alice 검색
        alice_commits = self.index.search_by_author("Alice")
        self.assertEqual(len(alice_commits), 2)
        self.assertIn("h1", alice_commits)
        self.assertIn("h3", alice_commits)

        # 소문자로 검색해도 매칭되는지 검증
        alice_lower = self.index.search_by_author("alice")
        self.assertEqual(alice_lower, alice_commits)

        # 대문자로 검색해도 같은 작성자 색인에서 즉시 찾아야 함
        alice_upper = self.index.search_by_author("ALICE")
        self.assertEqual(alice_upper, alice_commits)


if __name__ == "__main__":
    unittest.main()
