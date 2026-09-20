# 프로그램을 실제로 조립하고 작은 입력부터 경계 조건까지 검사하는 회귀 테스트임.
import importlib  # 하이픈이 있는 패키지를 이름으로 불러옴.
import io  # 화면 출력을 메모리에 담음.
import unittest  # 파이썬 기본 테스트 도구를 불러옴.
from contextlib import redirect_stdout  # 테스트 중 출력만 잠시 모음.
from pathlib import Path  # 프로젝트 안의 임시 파일 경로를 만듦.
from tempfile import TemporaryDirectory  # 테스트 후 임시 폴더를 자동 정리함.
from unittest.mock import patch  # 사용자 입력과 파일 읽기를 안전하게 대신함.

app_module = importlib.import_module("git-app.__main__")  # 실제 실행 시작점을 불러옴.
from cli.parser import CommandParser  # 한 줄 명령을 해석하는 도구임.
from graph.traversal import GraphTraversal  # 그래프 탐색 도구임.
from index.inverted_index import InvertedIndex  # 단어와 작성자 색인임.
from models.commit import Commit  # 커밋 자료형임.
from repositories.commit_repository import CommitRepository  # 커밋 저장소임.
from sort.quick_sort import quick_sort  # 직접 만든 퀵 정렬임.
from validators.dag_validator import DAGValidator  # 순환 검사 도구임.
from utils.hash_generator import HashGenerator  # 해시 중복 방지 도구임.


class TestRegressionCases(unittest.TestCase):  # 발견한 문제가 다시 생기는지 검사함.
    def setUp(self):  # 각 검사마다 새 프로그램을 준비함.
        self.app = app_module.create_app()  # 메모리를 공유하지 않는 새 앱을 만듦.

    def run_line(self, line):  # 명령의 화면 출력과 계속 실행 여부를 받음.
        output = io.StringIO()  # 빈 출력 바구니를 만듦.
        with redirect_stdout(output):  # 이 명령의 출력만 모음.
            running = self.app.execute_line(line)  # 실제 명령을 실행함.
        return running, output.getvalue()  # 실행 상태와 글자를 돌려줌.

    def test_invalid_init_preserves_existing_state(self):  # 잘못된 초기화로 기록을 지우면 안 됨.
        self.run_line("INIT Alice")  # 정상 저장소를 만듦.
        self.run_line('COMMIT "keep me"')  # 지워지면 안 되는 기록을 만듦.
        _, output = self.run_line('INIT "   "')  # 공백뿐인 이름을 입력함.
        self.assertIn("Invalid args", output)  # 초기화가 거부되어야 함.
        self.assertIn("keep me", self.run_line("LOG")[1])  # 기존 기록이 남아야 함.
        self.assertIn("keep me", self.run_line("SEARCH --author=Alice")[1])  # 색인도 남아야 함.

    def test_parser_preserves_literal_quotes(self):  # 내용에 포함된 따옴표를 지우면 안 됨.
        command = "COMMIT \"'quoted'\""  # 큰따옴표 안의 작은따옴표는 메시지 내용임.
        self.assertEqual(CommandParser.parse_line(command)[1], ["'quoted'"])  # 원문을 보존함.
        command = "SEARCH --author=\"'Alice'\""  # 작성자 이름의 문자도 보존함.
        self.assertEqual(CommandParser.parse_line(command)[2]["author"], "'Alice'")  # 옵션값을 보존함.

    def test_malformed_options_are_rejected(self):  # 빠진 값과 중복 옵션을 검사함.
        self.run_line("INIT Alice")  # 빈 저장소에서도 문법을 검사해야 함.
        commands = [  # 잘못된 옵션 사례를 하나씩 모음.
            "SEARCH --author",  # 작성자 값이 빠짐.
            "LOG --sort-by",  # 정렬 기준 값이 빠짐.
            "LOG --sort-by=",  # 등호 뒤 값이 비어 있음.
            "LOG --sort-by=wrong",  # 지원하지 않는 정렬 기준임.
            "LOG --sort-by=date --sort-by=author",  # 기준을 중복해서 지정함.
        ]  # 검사할 입력 목록을 마무리함.
        for command in commands:  # 각 사례를 따로 실행함.
            with self.subTest(command=command):  # 어느 입력이 실패했는지 구분함.
                self.assertIn("Invalid args", self.run_line(command)[1])  # 표준 오류를 확인함.

    def test_invalid_exit_does_not_exit(self):  # 실수로 인자를 붙였을 때 종료를 막음.
        running, output = self.run_line("QUIT extra")  # 허용하지 않는 인자를 붙임.
        self.assertTrue(running)  # 앱이 계속 실행되어야 함.
        self.assertIn("Invalid args", output)  # 입력 오류를 알려야 함.

    def test_hybrid_input_and_option_end_marker(self):  # 대화형 입력과 옵션 구분 종료를 검사함.
        with patch("builtins.input", return_value="Alice Example"):  # 사용자의 이름 답변을 대신함.
            self.assertIn("Alice Example", self.run_line("INIT")[1])  # 질문 후 정상 초기화함.
        with patch("builtins.input", return_value="hello world"):  # 사용자의 메시지 답변을 대신함.
            self.assertIn("hello world", self.run_line("COMMIT")[1])  # 질문 후 커밋을 만듦.
        self.assertIn("--literal", self.run_line('COMMIT -- "--literal"')[1])  # 옵션처럼 생긴 메시지도 저장함.

    def test_directed_false_keeps_undirected_path(self):  # false를 true처럼 다루면 안 됨.
        self.run_line("INIT Alice")  # 새 저장소를 준비함.
        self.run_line("COMMIT root")  # 부모를 만듦.
        self.run_line("COMMIT child")  # 자식을 만듦.
        commits = self.app._dispatcher._git._commit_repo.find_all()  # 실행에서 만든 해시를 가져옴.
        command = f"PATH {commits[0].hash} {commits[1].hash}"  # 부모에서 자식으로 이동함.
        self.assertIn("No path", self.run_line(command + " --directed")[1])  # 부모 방향만이면 못 감.
        self.assertIn("Path:", self.run_line(command + " --directed=false")[1])  # 무방향이면 갈 수 있음.
        self.assertIn("Invalid args", self.run_line(command + " --directed=maybe")[1])  # 잘못된 값은 거부함.

    def test_repository_rejects_overwrite_and_missing_parent(self):  # 이미 저장한 역사와 부모 관계를 보호함.
        repository = CommitRepository()  # 빈 커밋 저장소를 만듦.
        repository.save(Commit("a", "root", "Alice"))  # 첫 기록을 저장함.
        with self.assertRaises(ValueError):  # 같은 번호 덮어쓰기는 실패해야 함.
            repository.save(Commit("a", "replacement", "Bob"))  # 기존 기록과 같은 번호를 씀.
        with self.assertRaises(ValueError):  # 존재하지 않는 부모는 실패해야 함.
            repository.save(Commit("b", "orphan", "Bob", parents=["missing"]))  # 없는 부모를 지정함.
        self.assertEqual(repository.count(), 1)  # 실패한 저장은 데이터에 영향을 주지 않아야 함.

    def test_topological_sort_rejects_incomplete_graph(self):  # 잘못된 그래프를 정상 로그처럼 출력하면 안 됨.
        commits = {"a": Commit("a", "cycle", "A", parents=["a"])}  # 자기 자신으로 돌아가는 순환임.
        with self.assertRaises(ValueError):  # 정렬할 수 없다고 알려야 함.
            GraphTraversal.topological_sort(commits)  # 기본 위상 정렬을 실행함.
        commits["a"].parents = ["missing"]  # 존재하지 않는 부모로 바꿔 봄.
        self.assertFalse(DAGValidator.validate(commits))  # 불완전한 그래프는 유효하지 않음.

    def test_deep_graph_does_not_hit_recursion_limit(self):  # 긴 역사도 재귀 오류 없이 검사함.
        commits = {}  # 최신 커밋부터 넣는 딕셔너리를 준비함.
        for number in range(1500, 0, -1):  # 호출 스택 제한보다 긴 역사를 만듦.
            parents = []  # 맨 처음 기록은 부모가 없음.
            if number > 1:  # 첫 기록 뒤부터는 이전 기록이 부모임.
                parents = [str(number - 1)]  # 이전 번호를 부모로 사용함.
            commits[str(number)] = Commit(str(number), "record", "A", parents=parents)  # 기록을 넣음.
        self.assertTrue(DAGValidator.validate(commits))  # 정상적인 긴 DAG를 받아야 함.

    def test_ancestors_deduplicates_shared_merge_parent(self):  # 같은 HEAD 두 개를 병합해도 조상은 한 번만 출력함.
        commits = {  # 같은 부모가 두 번 적힌 병합 그래프임.
            "a": Commit("a", "root", "A"),  # 첫 부모를 만듦.
            "b": Commit("b", "merge", "A", parents=["a", "a"]),  # 같은 부모를 두 번 지정함.
        }  # 그래프 구성을 마무리함.
        self.assertEqual(GraphTraversal.get_ancestors(commits, "b"), ["a"])  # 같은 조상을 중복 출력하지 않음.

    def test_path_ties_and_disconnected_roots(self):  # 동률 경로의 문자열 순서와 연결 없음을 검사함.
        commits = {  # 삽입 순서를 사전순과 다르게 만든 그래프임.
            "s": Commit("s", "root", "A"),  # 공통 뿌리임.
            "c10": Commit("c10", "right", "A", parents=["s"]),  # 뒤쪽 경로를 먼저 넣음.
            "c1": Commit("c1", "left", "A", parents=["s"]),  # 먼저인 경로를 나중에 넣음.
            "t": Commit("t", "merge", "A", parents=["c10", "c1"]),  # 두 경로의 도착점임.
            "other": Commit("other", "root", "A"),  # 연결 없는 별도 뿌리임.
        }  # 그래프 구성을 마무리함.
        self.assertEqual(GraphTraversal.bfs_shortest_path(commits, "s", "t"), ["s", "c1", "t"])  # 문자열이 앞선 경로를 선택함.
        self.assertIsNone(GraphTraversal.bfs_shortest_path(commits, "s", "other"))  # 다른 뿌리로는 갈 수 없음.
        self.assertEqual(GraphTraversal.bfs_shortest_path(commits, "s", "s"), ["s"])  # 자기 자신은 0걸음임.

    def test_quick_sort_long_ordered_input(self):  # 정렬된 긴 입력에서도 재귀 오류가 없어야 함.
        numbers = list(range(1500))  # 첫 원소 피벗의 최악 입력을 만듦.
        self.assertEqual(quick_sort(numbers), numbers)  # 모든 숫자가 그대로 나와야 함.

    def test_quick_sort_stability_in_both_directions(self):  # 이 구현의 실제 안정성을 확인함.
        records = [(2, "first"), (1, "low"), (2, "second")]  # 같은 점수에 서로 다른 이름을 붙임.
        for reverse in (False, True):  # 오름차순과 내림차순을 모두 검사함.
            result = quick_sort(records, key=self.record_score, reverse=reverse)  # 점수만 비교함.
            equal_records = []  # 동점자만 모음.
            for record in result:  # 결과를 순서대로 확인함.
                if record[0] == 2:  # 동점인 2점 기록만 고름.
                    equal_records.append(record[1])  # 이름의 상대 순서를 보관함.
            self.assertEqual(equal_records, ["first", "second"])  # 원래 순서를 유지해야 함.

    @staticmethod  # 테스트 자료에서 정렬 기준만 꺼내는 함수임.
    def record_score(record):  # 첫 칸의 점수를 비교 기준으로 씀.
        return record[0]  # 점수를 반환함.

    def test_index_duplicates_and_missing_word(self):  # 중복 단어와 다중 검색을 검사함.
        index = InvertedIndex()  # 빈 색인을 준비함.
        index.add_commit("a", "Hello hello world", "Alice")  # 중복된 단어가 있는 커밋을 넣음.
        index.add_commit("a", "Hello hello world", "Alice")  # 같은 커밋을 한 번 더 등록함.
        self.assertEqual(index.search_by_keyword("world HELLO"), ["a"])  # 한 번만 반환해야 함.
        self.assertEqual(index.search_by_author("ALICE"), ["a"])  # 작성자 색인도 중복이 없어야 함.
        self.assertEqual(index.search_by_keyword("hello missing"), [])  # 한 단어가 없으면 결과도 없음.

    def test_diff_blocks_symlink_to_sensitive_file(self):  # 이름을 바꾼 링크로 비밀 파일 차단을 피할 수 없어야 함.
        with TemporaryDirectory(dir=Path(__file__).parent) as directory:  # 프로젝트 안에만 임시 폴더를 만듦.
            folder = Path(directory)  # 폴더 경로를 준비함.
            secret = folder / ".env.example-test"  # 진짜 비밀값이 없는 가짜 파일 이름임.
            secret.write_text("test placeholder", encoding="utf-8")  # 비밀이 아닌 테스트 글자만 씀.
            alias = folder / "ordinary.txt"  # 평범해 보이는 링크 이름임.
            alias.symlink_to(secret.name)  # 가짜 환경 파일을 가리키게 함.
            with patch("services.bonus_service.SimpleDiff.diff_files") as reader:  # 실제 파일 읽기를 막음.
                result = self.app._dispatcher._bonus.diff_files(str(alias), str(alias))  # 우회 시도를 실행함.
                self.assertFalse(result[0])  # 비교를 거부해야 함.
                reader.assert_not_called()  # 파일 내용에 접근하기 전에 막아야 함.

    def test_repeated_hash_collision_has_finite_fallback(self):  # 고장 난 난수 생성기라도 실행이 끝나야 함.
        generator = HashGenerator()  # 기본 생성기를 만듦.
        issued = set()  # 발급한 번호를 저장소처럼 기억함.
        with patch.object(generator, "next_hash", return_value="same"):  # 같은 후보만 나오는 충돌을 강제함.
            first = generator.next_unique_hash("one", issued.__contains__)  # 첫 번호는 쓸 수 있음.
            issued.add(first)  # 이미 사용했다고 표시함.
            second = generator.next_unique_hash("two", issued.__contains__)  # 반복 충돌에서 탈출해야 함.
            issued.clear()  # INIT으로 저장소를 비우는 상황을 흉내 냄.
            third = generator.next_unique_hash("three", issued.__contains__)  # 발급한 번호를 다시 쓰면 안 됨.
        self.assertEqual(len({first, second, third}), 3)  # 세 번호가 모두 달라야 함.

    def test_two_roots_print_no_path_and_unknown_commit(self):  # 명령만으로 연결 없는 그래프를 만듦.
        self.run_line("INIT Alice")  # 커밋 없는 main을 만듦.
        self.run_line("BRANCH empty")  # 커밋이 없는 다른 가지도 만듦.
        self.run_line("COMMIT first")  # main의 첫 뿌리를 만듦.
        self.run_line("SWITCH empty")  # 아직 커밋 없는 가지로 이동함.
        self.run_line("COMMIT second")  # 다른 뿌리를 만듦.
        commits = self.app._dispatcher._git._commit_repo.find_all()  # 두 번호를 가져옴.
        command = f"PATH {commits[0].hash} {commits[1].hash}"  # 뿌리 사이를 찾음.
        self.assertEqual(self.run_line(command)[1].strip(), "No path")  # 연결이 없음을 출력함.
        self.assertIn("Unknown commit: missing", self.run_line(f"PATH missing {commits[0].hash}")[1])  # 없는 번호는 다른 오류임.

    def test_sort_by_author_and_date_are_distinct(self):  # 같은 작성자뿐인 기존 검사의 빈틈을 채움.
        self.run_line("INIT Zed")  # 사전순으로 뒤인 작성자로 시작함.
        self.run_line("COMMIT parent")  # 부모 커밋을 만듦.
        git = self.app._dispatcher._git  # 실제 서비스에 접근함.
        git._branch_repo.set_author("Alice")  # 평가용으로 다음 작성자를 바꿈.
        self.run_line("COMMIT child")  # 작성자순으로 앞서는 자식을 만듦.
        commits = git._commit_repo.find_all()  # 시간을 고정할 커밋 목록임.
        commits[0].timestamp = "2026-01-01 00:00:00"  # 부모의 시각을 고정함.
        commits[1].timestamp = "2026-01-02 00:00:00"  # 자식은 하루 뒤로 정함.
        log = self.run_line("LOG")[1]  # 기본 로그를 받음.
        self.assertLess(log.index("parent"), log.index("child"))  # 기본 로그는 부모 우선임.
        log = self.run_line("LOG --sort-by=author")[1]  # 작성자순 로그를 받음.
        self.assertLess(log.index("child"), log.index("parent"))  # 작성자순은 Alice 우선임.
        log = self.run_line("LOG --sort-by=date")[1]  # 날짜순 로그를 받음.
        self.assertLess(log.index("parent"), log.index("child"))  # 날짜순은 과거 우선임.

    def test_index_search_never_scans_all_commits(self):  # 검색할 때 전체 저장소를 읽지 않는지 검사함.
        self.run_line("INIT Alice")  # 저장소를 만듦.
        self.run_line('COMMIT "hello world"')  # 검색할 메시지를 만듦.
        repository = self.app._dispatcher._git._commit_repo  # 실제 커밋 저장소임.
        with patch.object(repository, "find_all", side_effect=AssertionError("Full scan")):  # 전체 순회를 금지함.
            self.assertIn("hello world", self.run_line("SEARCH hello")[1])  # 키워드 검색은 성공해야 함.
            self.assertIn("hello world", self.run_line("SEARCH --author=Alice")[1])  # 작성자 검색도 성공해야 함.

    def test_layered_graph_with_many_equal_paths(self):  # 갈림길이 반복되어도 경로를 하나만 골라야 함.
        commits = {"root": Commit("root", "start", "A")}  # 시작 커밋을 만듦.
        previous = "root"  # 이전 합류 지점을 기억함.
        expected = [previous]  # 정답 경로의 시작 번호임.
        for number in range(12):  # 12번 갈라지고 합쳐져 최단 경로가 4096개임.
            left = f"a{number:02}"  # 사전순으로 먼저인 가지임.
            right = f"b{number:02}"  # 사전순으로 나중인 가지임.
            merged = f"m{number:02}"  # 두 가지가 합쳐지는 곳임.
            commits[right] = Commit(right, "right", "A", parents=[previous])  # 뒤쪽 가지부터 저장함.
            commits[left] = Commit(left, "left", "A", parents=[previous])  # 입력 순서가 답을 결정하면 안 됨.
            commits[merged] = Commit(merged, "merge", "A", parents=[right, left])  # 합류 지점을 만듦.
            expected.extend([left, merged])  # 정답은 매번 왼쪽 가지임.
            previous = merged  # 다음 갈림길의 시작으로 옮김.
        self.assertEqual(GraphTraversal.bfs_shortest_path(commits, "root", previous), expected)  # 전체 경로가 맞아야 함.

    def test_real_entry_points_and_eof(self):  # 메서드 호출뿐 아니라 실제 프로그램 실행을 검사함.
        import os  # 자식 프로세스에 필요한 실행 환경을 준비함.
        import subprocess  # 실제 Python 실행기를 별도 프로세스로 실행함.
        import sys  # 현재 테스트와 같은 Python 실행기를 찾음.
        environment = dict(os.environ)  # 기존 환경을 복사하되 출력하지 않음.
        environment["PYTHONDONTWRITEBYTECODE"] = "1"  # 캐시 파일을 만들지 않게 함.
        commands = [[sys.executable, "-m", "git-app"], [sys.executable, "git-app/__main__.py"]]  # 두 시작 방법임.
        for command in commands:  # 각각 별도 프로그램으로 실행함.
            result = subprocess.run(  # 실제 시작 파일과 입력 끝 EOF를 검사함.
                command,  # 실행할 Python 명령임.
                input='INIT Alice\nCOMMIT "live entry"\nLOG\n',  # 순서대로 입력할 명령임.
                text=True,  # 입출력을 글자로 다룸.
                capture_output=True,  # 테스트가 결과를 검사하도록 출력을 모음.
                cwd=Path(__file__).resolve().parents[1],  # 프로젝트 폴더에서 실행함.
                env=environment,  # 캐시 쓰기를 끈 환경을 전달함.
                timeout=5,  # 프로그램이 멈추면 무한히 기다리지 않음.
            )  # 별도 프로세스 실행을 마무리함.
            self.assertEqual(result.returncode, 0)  # 정상 종료해야 함.
            self.assertIn("mini-git>", result.stdout)  # 실제 입력 프롬프트를 확인함.
            self.assertIn("live entry", result.stdout)  # 실제 로그가 출력되어야 함.
            self.assertEqual(result.stderr, "")  # 내부 오류를 출력하면 안 됨.

    def test_valid_reinitialization_clears_all_stores(self):  # 정상 INIT은 모든 기록을 함께 비워야 함.
        self.run_line("INIT Alice")  # 첫 저장소를 만듦.
        self.run_line("COMMIT hello")  # 검색할 기록을 만듦.
        self.run_line("BRANCH feature")  # 이전 가지도 만듦.
        self.run_line("INIT Bob")  # 새 작성자로 저장소를 초기화함.
        self.assertIn("No commits yet", self.run_line("LOG")[1])  # 기록이 비어야 함.
        self.assertIn("No commits found", self.run_line("SEARCH hello")[1])  # 키워드 색인도 비어야 함.
        self.assertIn("No commits found", self.run_line("SEARCH --author=Alice")[1])  # 작성자 색인도 비어야 함.
        self.assertIn("Unknown branch", self.run_line("SWITCH feature")[1])  # 옛 가지도 없어야 함.
        self.assertIn("[main ", self.run_line("COMMIT fresh")[1])  # 새 main에서 정상 커밋할 수 있어야 함.

    def test_interactive_cancellation_does_not_mutate(self):  # 질문 도중 취소해도 잘못된 커밋을 만들면 안 됨.
        self.run_line("INIT Alice")  # 앱을 초기화함.
        with patch("builtins.input", side_effect=EOFError):  # 입력 스트림 종료를 흉내 냄.
            self.assertIn("Invalid args", self.run_line("COMMIT")[1])  # 입력이 없었다고 알려야 함.
        self.assertIn("No commits yet", self.run_line("LOG")[1])  # 기록을 만들지 않아야 함.

    def test_merge_updates_only_current_branch_and_both_indexes(self):  # 병합도 일반 커밋과 같은 저장 규칙을 지켜야 함.
        self.run_line("INIT Alice")  # 빈 저장소를 만듦.
        self.run_line("COMMIT root")  # 공통 부모를 만듦.
        self.run_line("BRANCH feature")  # 같은 커밋의 가지를 만듦.
        self.run_line("SWITCH feature")  # 새 가지로 이동함.
        self.run_line("COMMIT feature")  # 새 가지에 기록함.
        git = self.app._dispatcher._git  # 저장 상태를 확인할 서비스를 가져옴.
        feature_hash = git._branch_repo.get_head_commit_hash()  # feature의 끝 번호를 기억함.
        self.run_line("SWITCH main")  # 기본 가지로 돌아감.
        self.run_line("COMMIT main")  # 다른 가지의 끝을 만듦.
        main_hash = git._branch_repo.get_head_commit_hash()  # main의 병합 전 번호임.
        self.run_line("MERGE feature")  # 현재 main에 feature를 병합함.
        merged = git._commit_repo.find_by_hash(git._branch_repo.get_head_commit_hash())  # 병합 결과를 찾음.
        self.assertEqual(merged.parents, [main_hash, feature_hash])  # 두 HEAD가 정확한 부모여야 함.
        self.assertEqual(git._branch_repo.get_branch_commit("feature"), feature_hash)  # 대상 가지는 그대로임.
        self.assertIn(merged.hash, self.run_line("SEARCH merge")[1])  # 키워드 색인에 병합도 등록됨.
        self.assertIn(merged.hash, self.run_line("SEARCH --author=Alice")[1])  # 작성자 색인에도 등록됨.

    def test_benchmark_covers_multiple_input_sizes(self):  # 보너스 시간 비교가 여러 크기와 두 정렬을 포함해야 함.
        _, table = self.run_line("BENCH")  # 실제 명령을 실행함.
        self.assertIn("Merge Sort", table)  # 병합 정렬 결과가 있어야 함.
        self.assertIn("Quick Sort", table)  # 퀵 정렬 결과가 있어야 함.
        for size in ("100개", "500개", "1,000개", "3,000개"):  # 지정한 네 크기를 확인함.
            self.assertIn(size, table)  # 시간은 기계마다 달라도 행은 있어야 함.
