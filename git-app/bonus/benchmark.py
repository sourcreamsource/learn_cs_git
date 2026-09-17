# 무작위 정수 리스트 생성을 위해 random 모듈을 불러옴
import random
# 실행 시간 측정을 위해 time 모듈을 불러옴
import time
# 타입 힌트를 위해 Dict, List, Tuple을 불러옴
from typing import Dict, List, Tuple
# 직접 구현한 병합 정렬 함수를 불러옴
from sort.merge_sort import merge_sort
# 직접 구현한 퀵 정렬 함수를 불러옴
from sort.quick_sort import quick_sort


# 정렬 알고리즘 간의 성능을 데이터 크기별로 측정하고 비교하는 벤치마크 클래스임 (보너스 과제 3)
class SortBenchmark:
    # 지정한 크기별로 병합 정렬과 퀵 정렬의 실행 속도를 측정하는 함수임
    @staticmethod
    # 아래 작업을 이름으로 다시 호출할 수 있게 함수로 정의함.
    def run_benchmark(
        # 다음 단계에서 쓸 값을 계산하거나 꺼내 변수에 보관함.
        sizes: List[int] = [100, 500, 1000, 2000]
    # 앞에서 여러 줄로 적은 값이나 설정의 묶음을 마무리함.
    ) -> List[Dict[str, float]]:
        # 결과 레코드들을 담을 리스트임
        results: List[Dict[str, float]] = []

        # 각 크기별로 테스트를 수행함
        for size in sizes:
            # 지정된 크기만큼의 난수 데이터셋을 생성함
            dataset: List[int] = []
            # 필요한 개수만큼 난수를 하나씩 목록에 추가함
            for number_index in range(size):
                # 1부터 100000 사이 난수 하나를 목록에 추가함
                dataset.append(random.randint(1, 100000))

            # 1. 병합 정렬(Merge Sort) 시간 측정
            merge_data = list(dataset)
            # 다음 단계에서 쓸 값을 계산하거나 꺼내 변수에 보관함.
            start_m = time.perf_counter()
            # 준비한 값으로 이 단계의 작업을 실행함.
            merge_sort(merge_data)
            # 다음 단계에서 쓸 값을 계산하거나 꺼내 변수에 보관함.
            end_m = time.perf_counter()
            # 다음 단계에서 쓸 값을 계산하거나 꺼내 변수에 보관함.
            time_merge_ms = (end_m - start_m) * 1000.0

            # 2. 퀵 정렬(Quick Sort) 시간 측정
            quick_data = list(dataset)
            # 다음 단계에서 쓸 값을 계산하거나 꺼내 변수에 보관함.
            start_q = time.perf_counter()
            # 준비한 값으로 이 단계의 작업을 실행함.
            quick_sort(quick_data)
            # 다음 단계에서 쓸 값을 계산하거나 꺼내 변수에 보관함.
            end_q = time.perf_counter()
            # 다음 단계에서 쓸 값을 계산하거나 꺼내 변수에 보관함.
            time_quick_ms = (end_q - start_q) * 1000.0

            # 결과를 딕셔너리에 기록함
            results.append(
                # 준비한 값으로 이 단계의 작업을 실행함.
                {
                    # 이 항목의 이름과 사용할 값 또는 자료형을 지정함.
                    "size": size,
                    # 이 항목의 이름과 사용할 값 또는 자료형을 지정함.
                    "merge_sort_ms": round(time_merge_ms, 3),
                    # 이 항목의 이름과 사용할 값 또는 자료형을 지정함.
                    "quick_sort_ms": round(time_quick_ms, 3),
                # 앞에서 여러 줄로 적은 값이나 설정의 묶음을 마무리함.
                }
            # 앞에서 여러 줄로 적은 값이나 설정의 묶음을 마무리함.
            )

        # 결과 리스트를 반환함
        return results

    # 벤치마크 결과를 마크다운 표 형태의 문자열로 포맷팅하는 함수임
    @classmethod
    # 아래 작업을 이름으로 다시 호출할 수 있게 함수로 정의함.
    def format_table(cls, results: List[Dict[str, float]]) -> str:
        # 표 헤더 작성
        lines = [
            # 이번 작업에 전달하거나 가져올 항목을 지정함.
            "| 데이터 크기 (N) | Merge Sort (ms) | Quick Sort (ms) | 더 빠른 알고리즘 |",
            # 이번 작업에 전달하거나 가져올 항목을 지정함.
            "|---|---|---|---|",
        # 앞에서 여러 줄로 적은 값이나 설정의 묶음을 마무리함.
        ]
        # 각 결과 행을 추가함
        for row in results:
            # 다음 단계에서 쓸 값을 계산하거나 꺼내 변수에 보관함.
            size = row["size"]
            # 다음 단계에서 쓸 값을 계산하거나 꺼내 변수에 보관함.
            m_ms = row["merge_sort_ms"]
            # 다음 단계에서 쓸 값을 계산하거나 꺼내 변수에 보관함.
            q_ms = row["quick_sort_ms"]
            # 기본 결과는 두 알고리즘 속도가 같다는 뜻으로 둠
            winner = "동률"
            # 병합 정렬 시간이 더 작으면 병합 정렬을 승자로 기록함
            if m_ms < q_ms:
                # 다음 단계에서 쓸 값을 계산하거나 꺼내 변수에 보관함.
                winner = "Merge Sort"
            # 퀵 정렬 시간이 더 작으면 퀵 정렬을 승자로 기록함
            elif q_ms < m_ms:
                # 다음 단계에서 쓸 값을 계산하거나 꺼내 변수에 보관함.
                winner = "Quick Sort"
            # 찾은 항목을 목록 끝에 추가하여 기억함.
            lines.append(f"| {size:,}개 | {m_ms:.3f} ms | {q_ms:.3f} ms | {winner} |")

        # 완성된 표 문자열을 반환함
        return "\n".join(lines)
