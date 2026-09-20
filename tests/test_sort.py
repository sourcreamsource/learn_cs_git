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
# 직접 구현한 병합 정렬 함수를 불러옴
from sort.merge_sort import merge_sort
# 직접 구현한 퀵 정렬 함수를 불러옴
from sort.quick_sort import quick_sort


# 튜플의 두 번째 값을 나이 정렬 기준으로 반환하는 테스트용 함수임
def get_record_age(record):
    # 전달받은 튜플에서 나이 값을 반환함
    return record[1]


# 튜플의 두 번째 값을 점수 정렬 기준으로 반환하는 테스트용 함수임
def get_student_score(student):
    # 전달받은 튜플에서 점수 값을 반환함
    return student[1]


# 직접 구현한 정렬 알고리즘(Merge Sort, Quick Sort)의 정확성 및 안정성을 검증하는 테스트 클래스임
class TestSortingAlgorithms(unittest.TestCase):
    # 기본 숫자 정렬 테스트임
    def test_numeric_sorting(self):
        numbers = [5, 2, 9, 1, 5, 6]
        expected = [1, 2, 5, 5, 6, 9]

        sorted_m = merge_sort(numbers)
        self.assertEqual(sorted_m, expected)

        sorted_q = quick_sort(numbers)
        self.assertEqual(sorted_q, expected)

    # 내림차순 정렬 테스트임
    def test_reverse_sorting(self):
        numbers = [3, 1, 4, 1, 5, 9]
        expected = [9, 5, 4, 3, 1, 1]

        sorted_m = merge_sort(numbers, reverse=True)
        self.assertEqual(sorted_m, expected)

        sorted_q = quick_sort(numbers, reverse=True)
        self.assertEqual(sorted_q, expected)

    # key 함수를 활용한 객체/튜플 정렬 테스트임
    def test_key_sorting(self):
        records = [("Alice", 30), ("Bob", 20), ("Charlie", 25)]
        # 나이(두 번째 원소) 기준 정렬
        sorted_by_age = merge_sort(records, key=get_record_age)
        self.assertEqual(
            sorted_by_age, [("Bob", 20), ("Charlie", 25), ("Alice", 30)]
        )

    # 병합 정렬의 '안정 정렬(Stable Sort)' 특성 검증 테스트임 (평가항목 3)
    def test_merge_sort_stability(self):
        # 동일한 키(점수 100점)를 가진 서로 다른 사람 목록
        students = [
            ("Alice", 100, "1번"),
            ("Bob", 90, "2번"),
            ("Charlie", 100, "3번"),
            ("David", 100, "4번"),
        ]
        # 점수 기준 정렬 수행
        sorted_students = merge_sort(students, key=get_student_score)

        # 100점 동점자들의 상대적 순서(Alice -> Charlie -> David)가 그대로 유지되어야 안정 정렬임!
        # 100점 학생 이름을 담을 빈 목록을 준비함
        score_100_students = []
        # 정렬된 학생을 하나씩 확인함
        for student in sorted_students:
            # 점수가 100점인 학생만 이름 목록에 추가함
            if student[1] == 100:
                score_100_students.append(student[0])
        self.assertEqual(score_100_students, ["Alice", "Charlie", "David"])


if __name__ == "__main__":
    unittest.main()
