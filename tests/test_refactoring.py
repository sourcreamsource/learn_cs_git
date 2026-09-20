import importlib  # 앱 시작점을 패키지 이름으로 불러옴.
import io  # 화면 출력을 메모리에 모음.
import unittest  # 표준 자동 테스트 도구임.
from contextlib import redirect_stdout  # 테스트 동안만 출력 위치를 바꿈.
from unittest.mock import patch  # 입력 질문이 실행되지 않아야 하는 경우를 검사함.

app_module = importlib.import_module("git-app.__main__")  # 기존 앱 생성 호출 경로를 사용함.
from models.commit import Commit  # 그래프 검사용 커밋 자료형임.
from validators.dag_validator import DAGValidator  # 분리 후에도 그래프 검사 의미가 같은지 확인함.
from validators.command_validator import validate_command_shape  # 부작용 없는 공통 입력 검사를 확인함.


class TestRefactoringBoundaries(unittest.TestCase):  # 파일 분리 후 책임 경계에서 생길 수 있는 오류를 검사함.
    def setUp(self):  # 검사마다 새 앱을 준비함.
        self.app = app_module.create_app()  # 새 저장소·색인·서비스를 연결함.

    def run_line(self, app, line):  # 지정한 앱에 명령을 넣고 출력만 반환함.
        output = io.StringIO()  # 이번 명령의 출력을 담음.
        with redirect_stdout(output):  # 다른 검사의 출력은 건드리지 않음.
            app.execute_line(line)  # 실제 명령 연결표를 거쳐 실행함.
        return output.getvalue()  # 화면에 나타난 문장을 반환함.

    def test_all_command_groups_reject_unknown_options_before_input(self):  # 모든 명령군에 공통 검사가 적용되어야 함.
        self.run_line(self.app, "INIT Alice")  # 상태 변화를 검사할 저장소를 준비함.
        self.run_line(self.app, "COMMIT unchanged")  # 보존되어야 할 기록을 만듦.
        before = self.run_line(self.app, "LOG")  # 검사 전 기록을 기억함.
        actions = ("INIT", "BRANCH", "SWITCH", "COMMIT", "LOG", "PATH", "ANCESTORS", "SEARCH", "MERGE", "DIFF", "BENCH", "HELP")  # 지원 명령 전체임.
        with patch("builtins.input", side_effect=AssertionError("Unexpected prompt")):  # 오류 입력 때문에 질문하면 실패시킴.
            for action in actions:  # 모든 담당자 경로를 거침.
                with self.subTest(action=action):  # 실패한 명령을 구분함.
                    output = self.run_line(self.app, action + " --unsupported=value")  # 없는 옵션을 붙임.
                    self.assertEqual(output.strip(), "Invalid args: unsupported option --unsupported")  # 같은 규칙으로 거부해야 함.
        self.assertEqual(self.run_line(self.app, "LOG"), before)  # 오류 처리 후 기록이 그대로여야 함.

    def test_command_validation_does_not_print_or_change_inputs(self):  # 검증기는 입력 검사만 해야 함.
        args = ["one", "two"]  # 인자가 너무 많은 예시임.
        options = {"wrong": "value"}  # 지원하지 않는 옵션 예시임.
        output = io.StringIO()  # 검증기가 출력하는지 확인할 바구니임.
        with redirect_stdout(output):  # 출력이 생기면 저장함.
            error = validate_command_shape(args, options, 1, ())  # 오류를 값으로 돌려받음.
        self.assertEqual(error, "Invalid args: too many arguments")  # 인자 수 검사가 먼저임.
        self.assertEqual(output.getvalue(), "")  # 화면 출력은 호출자에게 맡겨야 함.
        self.assertEqual(args, ["one", "two"])  # 입력 인자를 바꾸면 안 됨.
        self.assertEqual(options, {"wrong": "value"})  # 입력 옵션도 바꾸면 안 됨.

    def test_app_factory_keeps_sessions_separate(self):  # 조립 파일 이동으로 앱 상태가 섞이지 않아야 함.
        other = app_module.create_app()  # 독립된 두 번째 앱을 만듦.
        self.run_line(self.app, "INIT Alice")  # 첫 번째 앱의 작성자를 설정함.
        self.run_line(self.app, "COMMIT first-session")  # 첫 앱에만 기록함.
        self.run_line(other, "INIT Bob")  # 두 번째 앱은 다른 사용자로 초기화함.
        self.assertIn("No commits yet", self.run_line(other, "LOG"))  # 첫 앱의 기록이 없어야 함.
        self.assertIn("first-session", self.run_line(self.app, "LOG"))  # 둘째 앱 초기화가 첫 앱을 지우면 안 됨.
        self.assertIn("first-session", self.run_line(self.app, "SEARCH --author=Alice"))  # 색인도 첫 앱에서 유지됨.

    def test_shared_writer_rejects_invalid_destination_before_saving(self):  # 공통 저장자가 없는 가지를 거부해야 함.
        self.run_line(self.app, "INIT Alice")  # 기본 브랜치만 준비함.
        git = self.app._dispatcher._git  # 실제 저장 서비스를 가져옴.
        with self.assertRaises(ValueError):  # 잘못된 브랜치는 명확히 거부해야 함.
            git._writer.create("missing", "should-not-exist", "Alice", [])  # 존재하지 않는 가지에 저장을 시도함.
        self.assertEqual(git._commit_repo.count(), 0)  # 커밋만 덩그러니 저장되면 안 됨.
        self.assertIsNone(git._branch_repo.get_head_commit_hash())  # main의 끝도 그대로여야 함.
        self.assertEqual(git._index.search_by_keyword("should-not-exist"), [])  # 색인에 기록이 생기면 안 됨.

    def test_writer_copies_parent_list_and_rejects_missing_parent(self):  # 호출자가 부모 목록을 바꿔도 저장된 기록은 유지됨.
        self.run_line(self.app, "INIT Alice")  # 기록할 앱을 초기화함.
        self.run_line(self.app, "COMMIT root")  # 유효한 부모를 만듦.
        git = self.app._dispatcher._git  # 공통 저장자를 가져올 서비스임.
        root = git._branch_repo.get_head_commit_hash()  # 부모 번호를 기억함.
        parents = [root]  # 호출자 쪽에서 관리하는 목록임.
        child = git._writer.create("main", "child", "Alice", parents)  # 이 목록으로 새 커밋을 생성함.
        parents.clear()  # 호출자 목록을 비워 봄.
        self.assertEqual(child.parents, [root])  # 저장된 부모 정보는 그대로여야 함.
        with self.assertRaises(ValueError):  # 없는 부모로 저장하는 것도 거부해야 함.
            git._writer.create("main", "invalid-parent", "Alice", ["missing"])  # 잘못된 부모를 지정함.
        self.assertEqual(git._commit_repo.count(), 2)  # 실패한 커밋은 남지 않아야 함.
        self.assertEqual(git._branch_repo.get_head_commit_hash(), child.hash)  # HEAD도 성공한 커밋에 남아야 함.
        self.assertEqual(git._index.search_by_keyword("invalid-parent"), [])  # 실패한 메시지는 검색되지 않아야 함.

    def test_dag_cycle_check_and_full_validation_remain_distinct(self):  # 순환 여부와 부모 존재 검사를 구분함.
        commit = Commit("a", "incomplete", "Alice", parents=["missing"])  # 없는 부모를 가진 커밋임.
        commits = {"a": commit}  # 검사할 그래프임.
        self.assertFalse(DAGValidator.has_cycle(commits))  # 내부에 순환은 없음.
        self.assertFalse(DAGValidator.validate(commits))  # 하지만 완전한 DAG는 아님.
        self.assertEqual(commit.parents, ["missing"])  # 검증기가 원본을 고치면 안 됨.
        commit.parents.append("a")  # 자기 자신을 가리키는 순환도 넣음.
        self.assertTrue(DAGValidator.has_cycle(commits))  # 외부 부모가 있어도 내부 순환을 찾아야 함.
        self.assertEqual(commit.parents, ["missing", "a"])  # 순환 검사도 원본을 유지해야 함.
