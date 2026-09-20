# 시스템 파일 및 디렉토리 조작을 위해 os 모듈을 불러옴
import os
# 파이썬 시스템 런타임 모듈을 불러옴
import sys

# 프로젝트 내 git-app 디렉토리를 파이썬 모듈 검색 경로에 최우선 등록함
_git_app_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "git-app"
)
# 모듈 검색 경로 목록에 git-app 경로가 없으면 추가함
if _git_app_dir not in sys.path:
    # 검색 목록 맨 앞에 삽입하여 git-app 내부 패키지를 우선 탐색함
    sys.path.insert(0, _git_app_dir)

# 단위 테스트 프레임워크인 unittest 모듈을 불러옴
import unittest
# 커밋 모델 클래스를 불러옴
from models.commit import Commit
# 입력값 유효성 검증 클래스를 불러옴
from validators.input_validator import InputValidator
# DAG 사이클 검증 클래스를 불러옴
from validators.dag_validator import DAGValidator
# 메시지 상수를 불러옴
from constants.messages import ERROR_EMPTY_BRANCH_NAME


# 입력값 검증기(InputValidator)와 DAG 검증기(DAGValidator)를 검증하는 테스트 클래스임
class TestValidators(unittest.TestCase):
    # 작성자 유효성 검증 테스트임
    def test_validate_author(self):
        # 정상 작성자 이름 입력 시 통과해야 함
        is_valid, cleaned = InputValidator.validate_author("Alice")
        # 검증 결과가 참이어야 함
        self.assertTrue(is_valid)
        # 공백이 정돈된 작성자 이름이 반환되어야 함
        self.assertEqual(cleaned, "Alice")

        # 빈 문자열 입력 시 실패해야 함
        is_valid, msg = InputValidator.validate_author("")
        # 검증 결과가 거짓이어야 함
        self.assertFalse(is_valid)
        # 안내 에러 메시지가 반환되어야 함
        self.assertIn("author name is required", msg)

        # 공백만 있는 문자열 입력 시 실패해야 함
        is_valid, msg = InputValidator.validate_author("   ")
        # 검증 결과가 거짓이어야 함
        self.assertFalse(is_valid)
        # 안내 에러 메시지가 반환되어야 함
        self.assertIn("author name is required", msg)

    # 브랜치 이름 유효성 검증 테스트임
    def test_validate_branch_name(self):
        # 새로운 브랜치 이름 입력 시 통과해야 함
        is_valid, cleaned = InputValidator.validate_branch_name("feature-login")
        # 검증 결과가 참이어야 함
        self.assertTrue(is_valid)
        # 정돈된 브랜치명이 반환되어야 함
        self.assertEqual(cleaned, "feature-login")

        # 빈 문자열 입력 시 실패해야 함
        is_valid, msg = InputValidator.validate_branch_name("")
        # 검증 결과가 거짓이어야 함
        self.assertFalse(is_valid)
        # 빈 브랜치 안내 에러 메시지가 포함되어야 함
        self.assertEqual(msg, ERROR_EMPTY_BRANCH_NAME)

        # 공백이 포함된 브랜치 이름 입력 시 실패해야 함
        is_valid, msg = InputValidator.validate_branch_name("feature login")
        # 검증 결과가 거짓이어야 함
        self.assertFalse(is_valid)
        # 공백 불가 에러 메시지가 포함되어야 함
        self.assertIn("Branch name cannot contain spaces", msg)

    # 커밋 메시지 유효성 검증 테스트임
    def test_validate_commit_message(self):
        # 정상 커밋 메시지 입력 시 통과해야 함
        is_valid, cleaned = InputValidator.validate_commit_message("Initial commit")
        # 검증 결과가 참이어야 함
        self.assertTrue(is_valid)
        # 정돈된 메시지가 반환되어야 함
        self.assertEqual(cleaned, "Initial commit")

        # 빈 문자열 입력 시 실패해야 함
        is_valid, msg = InputValidator.validate_commit_message("")
        # 검증 결과가 거짓이어야 함
        self.assertFalse(is_valid)
        # 안내 에러 메시지가 포함되어야 함
        self.assertIn("Commit message cannot be empty", msg)

        # 공백만 있는 문자열 입력 시 실패해야 함
        is_valid, msg = InputValidator.validate_commit_message("   ")
        # 검증 결과가 거짓이어야 함
        self.assertFalse(is_valid)
        # 안내 에러 메시지가 포함되어야 함
        self.assertIn("Commit message cannot be empty", msg)

    # 정렬 옵션 유효성 검증 테스트임
    def test_validate_sort_option(self):
        # 정렬 옵션이 지정되지 않은 경우(None) 기본값 date로 통과해야 함
        is_valid, cleaned = InputValidator.validate_sort_option(None)
        # 검증 결과가 참이어야 함
        self.assertTrue(is_valid)
        # 기본 정렬 기준인 date가 반환되어야 함
        self.assertEqual(cleaned, "date")

        # date 정렬 옵션 입력 시 통과해야 함
        is_valid, cleaned = InputValidator.validate_sort_option("date")
        # 검증 결과가 참이어야 함
        self.assertTrue(is_valid)
        # 정돈된 정렬 기준인 date가 반환되어야 함
        self.assertEqual(cleaned, "date")

        # author 정렬 옵션 입력 시 통과해야 함
        is_valid, cleaned = InputValidator.validate_sort_option("author")
        # 검증 결과가 참이어야 함
        self.assertTrue(is_valid)
        # 정돈된 정렬 기준인 author가 반환되어야 함
        self.assertEqual(cleaned, "author")

        # 대소문자 혼합 옵션(Date) 입력 시 소문자로 정돈되어 통과해야 함
        is_valid, cleaned = InputValidator.validate_sort_option("Date")
        # 검증 결과가 참이어야 함
        self.assertTrue(is_valid)
        # 소문자 date로 정돈되어야 함
        self.assertEqual(cleaned, "date")

        # 지원하지 않는 정렬 옵션 입력 시 실패해야 함
        is_valid, msg = InputValidator.validate_sort_option("invalid_option")
        # 검증 결과가 거짓이어야 함
        self.assertFalse(is_valid)
        # 잘못된 정렬 옵션 안내 메시지가 포함되어야 함
        self.assertIn("Invalid sort option", msg)

    # DAG 무사이클 유효성 검증 테스트임
    def test_dag_validator_acyclic(self):
        # 빈 커밋 딕셔너리 검증 (사이클 없음)
        is_dag = DAGValidator.validate({})
        # DAG 검증 결과가 참이어야 함
        self.assertTrue(is_dag)
        # 사이클 검사도 거짓(False)이어야 함
        self.assertFalse(DAGValidator.has_cycle({}))

        # 단일 루트 커밋 노드 생성
        c1 = Commit(hash="c1", author="dev", message="root", parents=[])
        # 단일 노드 딕셔너리 구성
        single_commit = {"c1": c1}
        # DAG 검증 실행
        self.assertTrue(DAGValidator.validate(single_commit))
        # 사이클 없음 확인
        self.assertFalse(DAGValidator.has_cycle(single_commit))

        # 정상적인 선형 DAG 그래프: c1 -> c2 -> c3 (c2의 부모 c1, c3의 부모 c2)
        c2 = Commit(hash="c2", author="dev", message="second", parents=["c1"])
        c3 = Commit(hash="c3", author="dev", message="third", parents=["c2"])
        linear_commits = {"c1": c1, "c2": c2, "c3": c3}
        # DAG 검증 실행
        self.assertTrue(DAGValidator.validate(linear_commits))
        # 사이클 없음 확인
        self.assertFalse(DAGValidator.has_cycle(linear_commits))

        # 병합 커밋이 포함된 정상 분기-병합 DAG 그래프
        c_branch = Commit(hash="c_b", author="dev", message="feat", parents=["c1"])
        c_merge = Commit(hash="c_m", author="dev", message="merge", parents=["c2", "c_b"])
        merge_commits = {"c1": c1, "c2": c2, "c_b": c_branch, "c_m": c_merge}
        # DAG 검증 실행
        self.assertTrue(DAGValidator.validate(merge_commits))
        # 사이클 없음 확인
        self.assertFalse(DAGValidator.has_cycle(merge_commits))

    # DAG 사이클 탐지 테스트임
    def test_dag_validator_cycle_detection(self):
        # 자기 자신을 부모로 가리키는 사이클 커밋: c1 -> c1
        c_self = Commit(hash="c1", author="dev", message="self-cycle", parents=["c1"])
        self_cycle = {"c1": c_self}
        # 사이클이 존재하므로 DAG 검증은 거짓이어야 함
        self.assertFalse(DAGValidator.validate(self_cycle))
        # has_cycle 결과는 참이어야 함
        self.assertTrue(DAGValidator.has_cycle(self_cycle))

        # 3개 노드가 원형으로 순환하는 그래프: c1 -> c2 -> c3 -> c1
        c1 = Commit(hash="c1", author="dev", message="c1", parents=["c3"])
        c2 = Commit(hash="c2", author="dev", message="c2", parents=["c1"])
        c3 = Commit(hash="c3", author="dev", message="c3", parents=["c2"])
        circular_commits = {"c1": c1, "c2": c2, "c3": c3}
        # 사이클이 존재하므로 DAG 검증은 거짓이어야 함
        self.assertFalse(DAGValidator.validate(circular_commits))
        # has_cycle 결과는 참이어야 함
        self.assertTrue(DAGValidator.has_cycle(circular_commits))


# 메인 모듈 실행 시 unittest 러너 실행
if __name__ == "__main__":
    # 테스트 프레임워크 가동
    unittest.main()
