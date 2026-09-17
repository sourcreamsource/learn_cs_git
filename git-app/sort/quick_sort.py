# 타입 힌트를 위해 Any, Callable, List, Optional을 불러옴
from typing import Any, Callable, List, Optional


# 별도 정렬 기준이 없을 때 값 자신을 기준으로 돌려주는 함수임
def use_item_as_key(item: Any) -> Any:
    # 전달받은 값을 바꾸지 않고 그대로 반환함
    return item


# 피벗을 기준으로 작은 값과 큰 값을 분할하여 정렬하는 퀵 정렬(Quick Sort) 함수임 (평균 O(N log N), 최악 O(N^2))
def quick_sort(
    # 이 항목의 이름과 사용할 값 또는 자료형을 지정함.
    items: List[Any],
    # 이 항목의 이름과 사용할 값 또는 자료형을 지정함.
    key: Optional[Callable[[Any], Any]] = None,
    # 이 항목의 이름과 사용할 값 또는 자료형을 지정함.
    reverse: bool = False,
# 앞에서 여러 줄로 적은 값이나 설정의 묶음을 마무리함.
) -> List[Any]:
    # 원소가 1개 이하이면 이미 정렬된 상태이므로 복사본을 반환함
    if len(items) <= 1:
        # 처리 결과를 호출한 곳에 돌려주고 이 함수의 실행을 끝냄.
        return list(items)

    # 키 추출 함수가 없으면 자기 자신을 기본으로 지정함
    if key is None:
        # 이름이 있는 기본 키 함수를 지정하여 람다 문법을 몰라도 읽을 수 있게 함
        key = use_item_as_key

    # 작업 목록을 직접 사용하여 파이썬 재귀 깊이 제한을 피함.
    pending = [(list(items), False)]
    # 정렬이 끝난 조각을 차례로 담을 결과임.
    result: List[Any] = []
    # 처리할 조각이 남아 있는 동안 반복함.
    while pending:
        # 마지막에 넣은 작업부터 꺼냄. ready는 그대로 출력해도 된다는 표시임.
        group, ready = pending.pop()
        # 같은 값만 모인 조각이거나 원소가 하나뿐이면 바로 출력함.
        if ready or len(group) <= 1:
            # 이미 올바른 순서인 조각을 뒤에 붙임.
            result.extend(group)
            # 다음 작업으로 넘어감.
            continue
        # 첫 원소를 기준점으로 사용하므로 최악 시간은 여전히 O(N²)임.
        pivot_value = key(group[0])
        # 기준점보다 작은 원소를 모음.
        less = []
        # 같은 원소를 입력 순서대로 모아 안정성을 지킴.
        equal = []
        # 기준점보다 큰 원소를 모음.
        greater = []
        # 입력 순서대로 세 그룹에 나눔.
        for item in group:
            # 실제 비교할 값을 꺼냄.
            value = key(item)
            # 기준점보다 작으면 작은 그룹에 넣음.
            if value < pivot_value:
                # 작은 원소도 입력 순서를 유지함.
                less.append(item)
            # 기준점보다 크면 큰 그룹에 넣음.
            elif value > pivot_value:
                # 큰 원소도 입력 순서를 유지함.
                greater.append(item)
            # 같은 값은 같은 그룹에 모음.
            else:
                # 동점자의 순서를 바꾸지 않음.
                equal.append(item)
        # 스택은 나중에 넣은 것을 먼저 꺼내므로 출력의 반대 순서로 넣음.
        if reverse:
            # 내림차순에서 작은 그룹은 마지막에 출력함.
            pending.append((less, False))
            # 같은 그룹은 더 나누지 않아도 됨.
            pending.append((equal, True))
            # 큰 그룹을 다음에 처리함.
            pending.append((greater, False))
        # 기본 오름차순의 작업 순서임.
        else:
            # 큰 그룹을 마지막에 출력함.
            pending.append((greater, False))
            # 같은 그룹은 그대로 출력함.
            pending.append((equal, True))
            # 작은 그룹을 다음에 처리함.
            pending.append((less, False))
    # 입력 목록을 바꾸지 않고 새 정렬 결과를 반환함.
    return result
