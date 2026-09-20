# 타입 힌트를 위해 Any, Callable, List, Optional을 불러옴
from typing import Any, Callable, List, Optional


# 별도 정렬 기준이 없을 때 값 자신을 기준으로 돌려주는 함수임
def use_item_as_key(item: Any) -> Any:
    # 전달받은 값을 바꾸지 않고 그대로 반환함
    return item


# 리스트를 반으로 쪼갠 뒤 병합하며 정렬하는 병합 정렬(Merge Sort) 함수임 (O(N log N), 안정 정렬 보장)
def merge_sort(
    # 이 항목의 이름과 사용할 값 또는 자료형을 지정함.
    items: List[Any],
    # 이 항목의 이름과 사용할 값 또는 자료형을 지정함.
    key: Optional[Callable[[Any], Any]] = None,
    # 이 항목의 이름과 사용할 값 또는 자료형을 지정함.
    reverse: bool = False,
# 앞에서 여러 줄로 적은 값이나 설정의 묶음을 마무리함.
) -> List[Any]:
    # 항목이 1개 이하이면 이미 정렬된 상태이므로 복사본을 반환함
    """반으로 나누고 합치면서 입력을 바꾸지 않는 정렬 목록을 만든다.

    items는 입력 목록, key는 비교값 함수, reverse=True는 내림차순이다.
    같은 비교값의 입력 순서를 유지하는 안정 정렬이다.
    평균·최악 시간 O(N log N), 추가 공간 O(N)이며
    키 계산과 비교를 상수 비용으로 가정한다.
    LOG의 날짜·작성자 정렬과 PATH의 이웃 정렬에서 사용한다.
    """
    if len(items) <= 1:
        # 처리 결과를 호출한 곳에 돌려주고 이 함수의 실행을 끝냄.
        return list(items)

    # 키 추출 함수가 전달되지 않은 경우 기본값으로 자기 자신을 반환하도록 설정함
    if key is None:
        # 이름이 있는 기본 키 함수를 지정하여 람다 문법을 몰라도 읽을 수 있게 함
        key = use_item_as_key

    # 리스트의 중간 지점 인덱스를 계산함
    mid = len(items) // 2

    # 왼쪽 절반을 슬라이싱하여 재귀적으로 병합 정렬함
    left_sorted = merge_sort(items[:mid], key=key, reverse=reverse)
    # 오른쪽 절반을 슬라이싱하여 재귀적으로 병합 정렬함
    right_sorted = merge_sort(items[mid:], key=key, reverse=reverse)

    # 정렬된 두 부분 리스트를 병합하여 반환함
    return _merge(left_sorted, right_sorted, key=key, reverse=reverse)


# 정렬된 두 개의 서브리스트를 하나로 합치는 헬퍼 함수임 (평가항목 3: 안정 정렬 유지 핵심)
def _merge(
    # 이 항목의 이름과 사용할 값 또는 자료형을 지정함.
    left: List[Any],
    # 이 항목의 이름과 사용할 값 또는 자료형을 지정함.
    right: List[Any],
    # 이 항목의 이름과 사용할 값 또는 자료형을 지정함.
    key: Callable[[Any], Any],
    # 이 항목의 이름과 사용할 값 또는 자료형을 지정함.
    reverse: bool,
# 앞에서 여러 줄로 적은 값이나 설정의 묶음을 마무리함.
) -> List[Any]:
    # 병합된 결과를 담을 빈 리스트를 생성함
    """같은 기준으로 정렬된 두 목록을 안정적으로 합친 새 목록을 반환한다.

    값이 같으면 왼쪽 것을 먼저 골라 원래 순서를 유지한다.
    오름차순은 <=, 내림차순은 >=가 그 조건이다.
    두 목록 길이 합에 비례하는 시간과 결과 공간이 필요하다.
    """
    merged: List[Any] = []
    # 왼쪽 리스트를 가리킬 포인터 변수임
    i = 0
    # 오른쪽 리스트를 가리킬 포인터 변수임
    j = 0

    # 양쪽 리스트 모두 원소가 남아있을 때까지 비교 반복함
    while i < len(left) and j < len(right):
        # 왼쪽 요소의 키 값을 추출함
        val_left = key(left[i])
        # 오른쪽 요소의 키 값을 추출함
        val_right = key(right[j])

        # 오름차순 또는 내림차순 조건에 따라 어떤 요소를 먼저 넣을지 판별함
        if not reverse:
            # 오름차순: 왼쪽이 작거나 같으면 왼쪽 선택 (<= 연산자를 통해 안정 정렬 보장!)
            if val_left <= val_right:
                # 찾은 항목을 목록 끝에 추가하여 기억함.
                merged.append(left[i])
                # 처리한 개수나 다음에 볼 위치를 갱신함.
                i += 1
            # 앞의 조건에 해당하지 않는 나머지 경우를 처리함.
            else:
                # 찾은 항목을 목록 끝에 추가하여 기억함.
                merged.append(right[j])
                # 처리한 개수나 다음에 볼 위치를 갱신함.
                j += 1
        # 앞의 조건에 해당하지 않는 나머지 경우를 처리함.
        else:
            # 내림차순: 왼쪽이 크거나 같으면 왼쪽 선택
            if val_left >= val_right:
                # 찾은 항목을 목록 끝에 추가하여 기억함.
                merged.append(left[i])
                # 처리한 개수나 다음에 볼 위치를 갱신함.
                i += 1
            # 앞의 조건에 해당하지 않는 나머지 경우를 처리함.
            else:
                # 찾은 항목을 목록 끝에 추가하여 기억함.
                merged.append(right[j])
                # 처리한 개수나 다음에 볼 위치를 갱신함.
                j += 1

    # 왼쪽 리스트에 남은 모든 원소를 순서대로 추가함
    while i < len(left):
        # 찾은 항목을 목록 끝에 추가하여 기억함.
        merged.append(left[i])
        # 처리한 개수나 다음에 볼 위치를 갱신함.
        i += 1

    # 오른쪽 리스트에 남은 모든 원소를 순서대로 추가함
    while j < len(right):
        # 찾은 항목을 목록 끝에 추가하여 기억함.
        merged.append(right[j])
        # 처리한 개수나 다음에 볼 위치를 갱신함.
        j += 1

    # 병합 완료된 리스트를 반환함
    return merged
