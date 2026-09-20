# 시스템 파일 및 디렉토리 조작을 위해 os 모듈을 불러옴
import os
# 표준 출력을 가로채기 위해 io 모듈을 불러옴
import io
# 표준 출력을 가로채기 위해 sys 모듈을 불러옴
import sys

# 프로젝트 내 git-app 디렉토리를 파이썬 모듈 검색 경로에 최우선 등록함
_git_app_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "git-app"
)
if _git_app_dir not in sys.path:
    sys.path.insert(0, _git_app_dir)
# 파이썬 동적 모듈 로더를 불러옴
import importlib.util
# 단위 테스트 프레임워크인 unittest 모듈을 불러옴
import unittest
from contextlib import redirect_stdout  # 테스트 중 출력만 임시로 모으고 자동 복원함.
from constants.messages import ERROR_NOT_INITIALIZED  # 초기화 전 오류 문구를 비교함.

# git-app/__main__.py 모듈 스펙을 생성함
_main_spec = importlib.util.spec_from_file_location(
    "git_app_main", os.path.join(_git_app_dir, "__main__.py")
)
# 모듈 객체 생성
_git_app_main = importlib.util.module_from_spec(_main_spec)
# 모듈 로드 실행
_main_spec.loader.exec_module(_git_app_main)
# create_app 함수 참조 가져오기
create_app = _git_app_main.create_app
# 명령 파서 클래스를 불러옴
from cli.parser import CommandParser


# CLI 명령어 파싱 및 하이브리드 REPL 실행 흐름을 검증하는 테스트 클래스임
class TestCLI(unittest.TestCase):
    def test_branch_list(self):  # 목록 조회와 현재 브랜치 표시 및 잘못된 입력을 검증함.
        cli = create_app()  # 독립된 테스트용 앱을 만듦.
        def execute(line):  # 명령 하나의 출력 결과를 얻는 도우미임.
            output = io.StringIO()  # 화면 출력을 담을 통을 만듦.
            with redirect_stdout(output):  # 이 명령의 출력만 통으로 보냄.
                cli.execute_line(line)  # 실제 명령 처리 과정을 실행함.
            return output.getvalue()  # 모은 출력 문자열을 반환함.
        self.assertEqual(execute("branch list"), ERROR_NOT_INITIALIZED + "\n")  # 초기화 전 조회를 막음.
        execute("init Alice")  # 기본 main 브랜치를 준비함.
        self.assertEqual(execute("branch list"), "* main\n")  # 커밋 없이도 기본 브랜치를 보여 줌.
        self.assertIn("Created branch: feature", execute("branch feature"))  # 기존 생성 기능을 확인함.
        execute("switch feature")  # 현재 브랜치를 바꿈.
        expected = "  main\n* feature\n"  # 전환 후 기대하는 목록임.
        self.assertEqual(execute("BrAnCh LiSt"), expected)  # 대소문자와 현재 위치 표시를 확인함.
        self.assertIn("Invalid args", execute("branch list extra"))  # 불필요한 인자를 거부함.
        self.assertIn("Invalid args", execute("branch list --author=Alice"))  # 지원하지 않는 옵션을 거부함.
        self.assertEqual(execute("branch list"), expected)  # 반복 조회나 잘못된 입력이 목록을 바꾸지 않음.
        self.assertIn("BRANCH LIST", execute("help"))  # 도움말에서도 새 명령을 찾을 수 있음.

    # 한 줄 명령어 파싱 기능 검증 테스트임
    def test_command_parser(self):
        # 1. 일반 명령 및 대소문자 무시 테스트
        action, args, opts = CommandParser.parse_line("init Alice")
        self.assertEqual(action, "INIT")
        self.assertEqual(args, ["Alice"])
        self.assertEqual(opts, {})

        # 2. 공백 및 따옴표 포함 인자 파싱 테스트
        action, args, opts = CommandParser.parse_line(
            'commit "Add payment feature"'
        )
        self.assertEqual(action, "COMMIT")
        self.assertEqual(args, ["Add payment feature"])

        # 3. 옵션 플래그 파싱 테스트
        action, args, opts = CommandParser.parse_line(
            "search --author=Alice"
        )
        self.assertEqual(action, "SEARCH")
        self.assertEqual(opts["author"], "Alice")

        action, args, opts = CommandParser.parse_line("log --sort-by=date")
        self.assertEqual(action, "LOG")
        self.assertEqual(opts["sort-by"], "date")

        # 닫히지 않은 따옴표는 원래 뜻을 추측하지 않고 파싱 오류가 되어야 함
        action, args, opts = CommandParser.parse_line('commit "unfinished')
        self.assertIsNone(action)
        self.assertEqual(opts["parse-error"], "unmatched quote")

    # 전체 CLI REPL의 한 줄 실행 흐름 및 출력 검증 테스트임
    def test_cli_execution_flow(self):
        cli = create_app()

        # 출력을 가로채기 위한 StringIO 객체 생성
        captured_output = io.StringIO()
        sys.stdout = captured_output

        try:
            # 1. 초기화 명령 실행
            cli.execute_line('INIT "Alice"')
            # 2. 첫 커밋 실행
            cli.execute_line('COMMIT "Initial commit"')
            # 3. 브랜치 생성 및 전환
            cli.execute_line("BRANCH feature")
            cli.execute_line("SWITCH feature")
            # 4. 두 번째 커밋
            cli.execute_line('COMMIT "Feature work"')
            # 5. LOG 실행
            cli.execute_line("LOG")
            # 6. 검색 실행
            cli.execute_line('SEARCH "feature"')
            # 7. 공백 포함 검색어가 모든 단어를 가진 커밋을 찾는지 확인함
            cli.execute_line('SEARCH "feature work"')
            # 8. 대소문자가 다른 작성자 옵션 검색이 같은 결과를 찾는지 확인함
            cli.execute_line("SEARCH --author=ALICE")
            # 9. 직접 구현한 작성자 정렬 로그가 실행되는지 확인함
            cli.execute_line("LOG --sort-by=author")
            # 10. 잘못 닫힌 따옴표가 실행되지 않고 표준 오류를 출력하는지 확인함
            cli.execute_line('COMMIT "unfinished')
            # 11. 종료 실행
            keep_running = cli.execute_line("QUIT")
            self.assertFalse(keep_running)
        finally:
            # 표준 출력 복원
            sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        # 출력 내용에 핵심 문구들이 포함되어 있는지 검증
        self.assertIn("Initialized repository.", output)
        self.assertIn("Created branch: feature", output)
        self.assertIn("Switched to branch: feature", output)
        self.assertIn("Initial commit", output)
        self.assertIn("Feature work", output)
        self.assertIn("Found 1 commit", output)
        # 작성자 색인 검색으로 두 커밋이 출력되어야 함
        self.assertIn("Found 2 commits", output)
        # 공백 포함 검색어의 결과가 출력에 포함되어야 함
        self.assertIn("- ", output)
        # 닫히지 않은 따옴표 입력의 표준 오류가 출력되어야 함
        self.assertIn("Invalid args: unmatched quote", output)


if __name__ == "__main__":
    unittest.main()
