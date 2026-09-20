from collections import deque  # 가까운 곳부터 확인하는 BFS 큐임.
from models.commit import Commit  # 그래프 노드의 자료형임.
from sort.merge_sort import merge_sort  # 이웃의 사전순 정렬에도 직접 구현한 정렬을 사용함.


# 경로 문자열의 구분자까지 포함해서 이웃을 비교함.
def path_step_key(commit_hash: str) -> str:
    return commit_hash + "->"  # 실제 경로 표기와 같은 비교 기준을 반환함.


# -------------------------------------------------------------------------------
# ✅
# 1. 저장된 부모 연결을 탐색용 이웃 목록으로 바꿈.
# 2. 동률 경로의 방문 순서를 고정함.
def _build_adjacency(commits: dict[str, Commit], directed: bool) -> dict[str, list[str]]:
    neighbors = {}  # 커밋 번호별로 이동할 수 있는 번호 목록임.
    
    for commit_hash in commits:  # 연결이 없는 커밋도 빈 목록을 갖게 함.
        neighbors[commit_hash] = []  # 아직 이웃을 넣지 않은 상태임.
    
    for commit_hash, commit in commits.items():  # 각 커밋의 부모 정보를 읽음.
        
        for parent in commit.parents:  # 부모가 여러 개일 수 있음.
            
            if parent not in commits:  # 없는 부모를 정상 연결처럼 처리하지 않음.
                raise ValueError(f"Unknown commit: {parent}")  # 불완전한 그래프를 알려 줌.
            neighbors[commit_hash].append(parent)  # 자식에서 부모로 가는 길을 넣음.
            
            if not directed:  # 기본 PATH는 양방향으로 이동할 수 있음.
                neighbors[parent].append(commit_hash)  # 부모에서 자식으로 가는 길도 넣음.
    
    for commit_hash in neighbors:  # 모든 이웃 목록을 정돈함.
        neighbors[commit_hash] = merge_sort(neighbors[commit_hash], key=path_step_key)  # 동률 경로의 방문 순서를 고정함.
    
    return neighbors  # 탐색에 사용할 연결 지도를 반환함.


# -------------------------------------------------------------------------------
# ✅
# 도착점에서 직전 번호를 따라 출발점까지 되짚음. 그리고 다시 reverse로 뒤집음.
def _restore_path(previous: dict[str, str | None], end: str) -> list[str]:
    path = []  # 거꾸로 찾은 경로를 담음.
    
    current = end  # 목적지에서 출발함.
    
    while current is not None:  # 출발점의 이전 번호인 None을 만날 때까지 이동함.
        path.append(current)  # 현재 번호를 경로에 추가함.
        current = previous[current]  # 직전에 방문했던 번호로 이동함.
    

    path.reverse()  # ✅ 출발점부터 읽도록 뒤집음. 정렬 API가 아님.
    
    return path  # 복원한 경로 하나를 반환함.




# -------------------------------------------------------------------------------
# ✅ 🔥🔥🔥🔥🔥 BFS(Breadth-First Search)로 가장 짧고 동률 중 사전순인 경로를 찾음.
# 핵심은 가장 가까이 있는 주변을 다 확인하는 방식이기 때문에 처음 찾는 것이 가장 짧은 경로임.
def bfs_shortest_path(commits: dict[str, Commit], start_hash: str, end_hash: str, directed: bool = False) -> list[str] | None:
    
    if start_hash not in commits or end_hash not in commits:  # 출발·도착 번호가 유효한지 확인함.
        return None  # 실제 오류 문구는 호출한 서비스가 결정함.
    
    if start_hash == end_hash:  # 같은 커밋 사이의 거리는 0임.
        return [start_hash]  # 커밋 하나로 끝나는 경로를 반환함.
    

    neighbors = _build_adjacency(commits, directed)  # 방향과 사전순을 반영한 지도를 준비함.
    # ✅ _build_adjacency 함수가 필요한 이유
    # 1. 양방향 이동을 지원하기 위해 부모 연결뿐 아니라 자식 방향으로의 연결도 미리 준비함.
    # 2. 최단 경로를 찾을 때 **거리가 똑같은 여러 갈래 길(동률 경로)**이 생길 수 있기 때문.
    #    파이썬 내부 메모리 상태에 따라 어떤 때는 a1b2c3를 먼저 방문하고, 어떤 때는 f9e8d7을 먼저 방문함.
    #    항상 사전에서 앞서는 a1b2c3 길을 먼저 탐색하도록 고정함.
    #    언제 실행하든 항상 똑같은 하나의 최단 경로를 반환함 (결정론적 일관성)
    

    ready = deque([start_hash])  # 출발점부터 가까운 거리 순서로 방문함.
    
    previous = {start_hash: None}  # 직전 번호와 방문 표시를 함께 기억함.
    
    while ready:  # 아직 확인할 커밋이 남아 있는 동안 반복함.
        current = ready.popleft()  # 현재 가장 가까운 후보를 꺼냄.
    
        # ✅ 목적지에 도착한다면, _restore_path 함수 작동 후 종료되는 조건문
        if current == end_hash:  
            return _restore_path(previous, end_hash)  # 저장해 둔 직전 번호로 경로를 복원함.
    
        # 🔥🔥🔥🔥🔥 핵심 : current의 주변 node를 모두 확인하는 것
        for neighbor in neighbors[current]:               # dict[str, list[str]] 사전순으로 이웃을 확인함.
            # dict[str, list[str]] 형태이며 key는 commit hash, value는 list of commit hash임.
            # 예시 : { 
            #    "a1b2c3": ["b2c3d4", "e4d3c2", "f1a2b3"],
            #    "b2c3d4": ["a1b2c3"],
            #    "e4d3c2": ["a1b2c3", "f1a2b3"],
            #    "f1a2b3": ["a1b2c3", "e4d3c2"]
            # }
            if neighbor not in previous:        # 처음 발견한 경우에만 방문 예약함.
                previous[neighbor] = current    # 이웃으로 가기 직전의 번호를 기억함.
                ready.append(neighbor)          # crrunt의 모든 주변을 확인했으므로 now ready는 crrunt의 주변 node를 담고, while문으로 다시 돌아감.

    return None  # 모든 연결을 확인해도 목적지를 만나지 못했음.






# -------------------------------------------------------------------------------
# ✅ 🔥🔥🔥🔥🔥 ANCESTORS 명령어
# 부모 방향으로만 BFS를 진행해 모든 조상을 중복 없이 반환함.
def get_ancestors(commits: dict[str, Commit], start_hash: str) -> list[str]:
    
    if start_hash not in commits:  # 대상 커밋이 존재하는지 확인함.
        return []  # 없는 번호의 오류 표시는 서비스에 맡김.
    
    visited = set()  # 이미 발견한 조상 번호를 기억함.
    
    result = []  # 조상을 발견한 순서를 유지함.
    
    ready = deque([start_hash])  # 대상 커밋의 부모부터 찾아 올라감.
    
    while ready:  # 아직 부모를 확인할 커밋이 남아 있음.
        current = ready.popleft()  # 다음 커밋을 꺼냄.
        for parent in commits[current].parents:  # 자식 방향으로 내려가지 않고 부모만 확인함.
            if parent in commits and parent not in visited:  # 존재하고 아직 보지 않은 조상만 처리함.
                visited.add(parent)  # 같은 조상을 다시 큐에 넣지 않도록 표시함.
                result.append(parent)  # 발견 순서대로 결과에 담음.
                ready.append(parent)  # 그 조상의 부모도 확인할 준비를 함.
    
    return result  # 전체 조상 번호를 발견 순서대로 반환함.
