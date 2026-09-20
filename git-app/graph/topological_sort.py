# topological_sort.py
# 유방향 무사이클 graph의 위상정렬(topological sort)

from collections import deque  # 앞에서 빠르게 꺼낼 준비 목록을 사용함.
from typing import Callable  # 작성자 우선순위를 정하는 함수의 자료형을 표시함.
from models.commit import Commit  # 그래프의 커밋 자료형임.


# ----------------------------------------------------------------------
# 부모 수와 부모별 자식 목록을 한 번에 준비함.
def _build_parent_links(commits: dict[str, Commit], ignore_missing: bool) -> tuple[dict[str, int], dict[str, list[str]]]:
    """위상 정렬에 필요한 남은 부모 수와 부모별 자식 목록을 만든다.

    입력 commits는 해시에서 Commit으로 연결되는 사전이다.
    저장된 자식 → 부모 관계로부터 처리용 부모 → 자식
    목록을 만든다. 반환값은 (남은 부모 수 사전, 자식 목록 사전)이다.
    없는 부모는 ValueError이며 ignore_missing=True일 때만 제외한다.
    """
    remaining = {}  # 커밋마다 아직 처리하지 않은 부모 수를 저장함.
    
    
    children = {}  # 각 부모가 처리된 뒤 찾아갈 자식을 저장함.
    
    
    for commit_hash in commits:  # 모든 커밋의 기본 칸을 만듦.
        remaining[commit_hash] = 0  # 부모 수는 연결을 보면서 셈.
        children[commit_hash] = []  # 아직 자식 관계를 기록하지 않은 상태임.
    
    
    for commit_hash, commit in commits.items():  # 각 커밋의 부모 관계를 읽음.
    
        for parent in commit.parents:  # 병합 커밋은 부모 두 개를 모두 셈.
    
            if parent not in commits:  # 없는 부모가 지정되었는지 확인함.
    
                if ignore_missing:  # 순환 여부만 검사할 때는 외부 연결을 무시함.
                    continue  # 그래프 내부 연결의 검사로 넘어감.
                raise ValueError(f"Unknown commit: {parent}")  # 일반 로그는 불완전한 그래프를 거부함.
    
    
            remaining[commit_hash] += 1  # 자식이 기다려야 할 부모 수를 늘림.
    
            children[parent].append(commit_hash)  # 부모를 처리한 뒤 알려 줄 자식을 등록함.
    
    
    return remaining, children  # 두 종류의 연결 정보를 함께 반환함.


# ----------------------------------------------------------------------
# 부모가 모두 처리된 후보 중 다음에 출력할 커밋 하나를 선택함.
def _take_next(ready: deque[str], commits: dict[str, Commit], priority: Callable[[Commit], str] | None) -> str:
    """부모 처리가 끝난 후보 중 다음 해시를 꺼낸다.

    priority가 None이면 큐 맨 앞을 O(1)에 꺼낸다.
    우선순위 함수가 있으면 준비된 후보만 비교한다.
    같은 값이면 먼저 들어온 후보를 유지하며 한 번 선택에 O(R)이 든다.
    R은 준비된 후보 수다. ready에서 선택한 해시를 제거하고 반환한다.
    """
    if priority is None:  # 기본 LOG는 준비된 순서대로 처리함.
        return ready.popleft()  # 기본 위상 정렬의 큐 꺼내기는 O(1)임.
    
    
    chosen = ready[0]  # 우선순위 비교의 첫 후보를 정함.
    
    
    best_value = priority(commits[chosen])  # 첫 후보의 작성자 등 비교값을 가져옴.
    
    
    for candidate in ready:  # 이미 부모가 처리된 후보들만 비교함.
        value = priority(commits[candidate])  # 이번 후보의 비교값을 구함.
        if value < best_value:  # 더 앞선 우선순위가 있으면 선택을 바꿈.
            chosen = candidate  # 새 후보의 번호를 기억함.
            best_value = value  # 다음 비교에 쓸 값을 갱신함.
    
    
    ready.remove(chosen)  # 선택한 후보를 대기 목록에서 제거함.
    
    
    return chosen  # 이번에 출력할 번호를 반환함.



# ====================================================================================================
# ✅ ❤️❤️❤️❤️❤️ 핵심 알고리즘
# Kahn 위상 정렬: 일반 LOG·작성자 우선 연습·DAG 검사가 같은 부모 처리 절차를 사용함.
def topological_sort(                                       # 기본 호출은 부모 우선 LOG와 같음.
    commits: dict[str, Commit],                             # 해시를 키로 가진 전체 커밋임.
    *,                                                      # 아래 설정은 이름을 붙여 명확히 전달함.
    priority_key: Callable[[Commit], str] | None = None,    # 준비된 후보끼리 비교할 선택 기준임.
    ignore_missing_parents: bool = False,                   # 순환만 검사할 때 외부 부모를 제외하는 설정임.
) -> list[Commit]:                                          # 부모가 먼저 오는 커밋 목록을 반환함.


    """Kahn 위상 정렬로 부모가 자식보다 먼저 오는 커밋 목록을 만든다.

    부모 수가 0인 커밋을 큐에서 꺼내고,
    그 자식의 남은 부모 수를 줄인다. 모두 0이 된 자식만 큐에 넣는다.
    입력 commits의 전체 그래프를 대상으로 하며 원본 커밋은 수정하지 않는다.
    없는 부모나 순환은 ValueError다. 빈 그래프의 결과는 빈 목록이다.
    ignore_missing_parents=True는 외부 부모를 무시하고 내부 순환을 검사한다.

    V는 커밋 수, E는 부모 연결 수다.
    기본 시간·추가 공간은 O(V+E)다. priority_key를 주면 준비된
    후보에서만 작은 값을 고르므로 부모 우선은 유지하지만 시간은
    최악 O(V²+E)다. 키 계산·비교 비용을 상수로 보는 설명이다.
    일반 작성자순 LOG의 병합 정렬과는 다른 기능이다.
    """
    remaining, children = _build_parent_links(commits, ignore_missing_parents)  # 부모 조건을 준비함.


    ready = deque()  # 지금 처리할 수 있는 커밋 목록임.


    for commit_hash, count in remaining.items():    # 각 커밋의 부모 수를 확인함.
        if count == 0:                              # 부모가 없는 커밋부터 시작함.
            ready.append(commit_hash)               # 즉시 처리할 후보에 넣음.
    
    
    result = []  # 부모 선후관계를 지킨 결과임.


    while ready:  # 출력 가능한 후보가 남아 있는 동안 진행함.
        current = _take_next(ready, commits, priority_key)  # 기본 순서 또는 선택 우선순위로 하나를 고름.
        
        result.append(commits[current])  # 선택한 커밋을 결과에 넣음.
        
        for child in children[current]:  # 이 부모를 기다리던 자식들을 확인함.
            remaining[child] -= 1  # 부모 하나의 처리가 끝났다고 표시함.
            if remaining[child] == 0:  # 모든 부모를 처리한 자식은 출력할 수 있음.
                ready.append(child)  # 다음 후보 목록에 넣음.



    # [검증 로직] 위 코드가 실행되었음에도 불구하고, 모든 노드를 처리하지 못했다면 사이클 형태라는 의미다.
    # (사이클은 처리될 수 없다. 에러 발생시키기!!!)
    if len(result) != len(commits):                         # 처리하지 못한 커밋이 남아 있으면 순환이 있음.
        raise ValueError("Invalid graph: cycle detected")   # 부분 로그를 정상 결과처럼 반환하지 않음.


    return result  # 부모가 먼저 출력되는 전체 순서를 반환함.





# ----------------------------------------------------------------------
# ✅ 그냥 rapper
# 기존 평가 연습 함수 이름으로 작성자 우선 위상 정렬을 호출함.
def topological_sort_with_priority(commits: dict[str, Commit], priority_key_func: Callable[[Commit], str]) -> list[Commit]:
    """부모 우선을 지키면서 준비된 후보의 우선순위로 위상 정렬한다.

    priority_key_func는 Commit에서 비교 문자열을 꺼내는 함수다.
    예를 들어 작성자를 기준으로 주어도 자식을 부모보다 먼저 내보내지 않는다.
    결과와 예외는 topological_sort를 그대로 따른다.
    현재 LOG --sort-by=author가 이 함수를 호출하는 것은 아니다.
    """
    return topological_sort(commits, priority_key=priority_key_func)  # 후보 선택 기준만 달리하고 정렬 절차는 공유함.
