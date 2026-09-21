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
    """부모 관계를 PATH용 이웃 사전으로 바꾼다.

    directed=False이면 자식 → 부모와 부모 → 자식을
    모두 넣는다. True이면 자식 → 부모만 넣어 조상 쪽 이동만 허용한다.
    원래 Commit.parents는 바꾸지 않는다. 없는 부모는 ValueError다.
    동률 최단 경로를 일정하게 고르도록 각 이웃 목록을 병합 정렬한다.
    이 준비 비용에는 그래프 순회뿐 아니라 이웃 정렬 비용도 포함된다.
    """
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
    """목적지부터 직전 방문 해시를 따라간 뒤 출발 순서로 뒤집는다.

    입력 previous는 BFS가 만든 직전 해시 사전이며 시작의 값은 None이다.
    end가 이 사전에 들어 있다는 전제에서 경로 목록을 반환한다.
    경로 길이를 L이라 하면 시간과 새 목록 공간은 O(L)이다.
    """
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
    
    """BFS(Breadth-First Search, 너비 우선 탐색)로 최단 경로를 찾는다.

    commits, 출발 해시, 도착 해시를 받아
    간선 개수가 가장 적은 해시 목록을 반환한다. 간선 가중치는 모두 같다.
    previous는 방문 표시와 직전 위치를 함께 기록하여 중복 예약을 막는다.
    큐에서 목적지를 꺼냈을 때 경로를 복원한다.
    없는 해시 또는 연결 없음은 None, 출발과 도착이 같으면 한 항목 목록이다.

    기본 directed=False는 부모·자식 양쪽 이동,
    True는 부모 쪽 이동만 허용한다. 예를 들어 A가 B의 부모라면
    방향 모드에서 B → A는 가능하지만 A → B는 불가능하다.
    순회 자체는 O(V+E)이며 전체 함수에는 이웃 정렬 준비 비용도 더해진다.
    서비스가 존재하지 않는 해시 오류와 정상적인 No path를 구분한다.
    """
    # [1. 이번 설명에서 사용할 원래 그래프]
    # graph = {                  # 이 예시는 '부모: 자식 목록'으로 읽음.
    #     "A": ["B", "C", "D"], # A의 자식은 B, C, D임.
    #     "B": ["E", "F"],      # B의 자식은 E, F임.
    #     "C": ["G"],           # C의 자식은 G임.
    #     "D": [],              # D에게는 자식이 없음.
    #     "E": [],              # E에게는 자식이 없음.
    #     "F": [],              # F에게는 자식이 없음.
    #     "G": [],              # G에게는 자식이 없음.
    # }                          # 아래 그림과 같은 연결 관계임.
    #             A
    #          /  |  \
    #         B   C   D
    #        / \  |
    #       E   F G
    # 주의: 원래 목록을 '화살표 방향으로만 이동 가능한 이웃'으로 해석하면
    # B에서는 E, F로만 갈 수 있으므로 D에 도달하지 못함.
    # 여기서는 기본값 directed=False, 즉 연결을 양방향으로 이동하는 경우를 설명함.
    # 따라서 B에서 부모 A로 올라간 뒤 A의 다른 자식 D로 내려갈 수 있음.

    # [2. 이 함수에 실제로 전달하는 commits의 모양]
    # 위 graph를 그대로 넘기면 안 됨. 이 함수는 리스트가 아닌 Commit 객체를 받음.
    # 실제 앱에서는 GraphService._get_commits_dict()가 저장소의 커밋을 모아 전달함.
    # Commit.parents에는 '자식 목록'이 아니라 '부모 해시 목록'이 들어감.
    # 따라서 같은 연결을 이 함수의 입력으로 표현하면 아래처럼 방향을 바꾸어 적음.
    # commits = {                                                   # 키는 해시, 값은 Commit 객체임.
    #     "A": Commit(hash="A", message="root", author="Kim", parents=[]),       # A는 부모가 없음.
    #     "B": Commit(hash="B", message="branch B", author="Kim", parents=["A"]), # B의 부모는 A임.
    #     "C": Commit(hash="C", message="branch C", author="Kim", parents=["A"]), # C의 부모는 A임.
    #     "D": Commit(hash="D", message="branch D", author="Kim", parents=["A"]), # D의 부모는 A임.
    #     "E": Commit(hash="E", message="child E", author="Kim", parents=["B"]),  # E의 부모는 B임.
    #     "F": Commit(hash="F", message="child F", author="Kim", parents=["B"]),  # F의 부모는 B임.
    #     "G": Commit(hash="G", message="child G", author="Kim", parents=["C"]),  # G의 부모는 C임.
    # }                                                             # 시각은 Commit의 기본값으로 채워짐.
    # bfs_shortest_path(commits, "B", "D")                           # B에서 D까지 양방향으로 찾는 호출임.
    # 이 호출에서 start_hash="B", end_hash="D", directed=False가 됨.
    # A~G는 설명용 짧은 해시임. 메시지·작성자·시각은 이 탐색의 비교 기준이 아님.

    # [3. 탐색을 시작할 수 있는 입력인지 검사]
    # 'B in commits'는 사전의 키 중 B가 있는지 검사함. Commit 내용 전체를 검색하지 않음.
    # 이번에는 B와 D가 모두 있으므로 아래 return None을 실행하지 않고 계속 진행함.
    if start_hash not in commits or end_hash not in commits:  # 출발·도착 번호가 유효한지 확인함.
        return None  # 실제 오류 문구는 호출한 서비스가 결정함.
    
    # B와 D는 다르므로 아래 즉시 반환도 건너뜀. B에서 B를 찾는 호출이면 ["B"]로 끝남.
    if start_hash == end_hash:  # 같은 커밋 사이의 거리는 0임.
        return [start_hash]  # 커밋 하나로 끝나는 경로를 반환함.
    

    neighbors = _build_adjacency(commits, directed)  # 방향과 사전순을 반영한 지도를 준비함.
    # [4. _build_adjacency가 반환한 neighbors의 실제 값]
    # neighbors = {              # 키는 현재 위치, 값은 한 번에 이동할 수 있는 모든 이웃임.
    #     "A": ["B", "C", "D"], # A에서 자식 B, C, D로 갈 수 있음.
    #     "B": ["A", "E", "F"], # B에서 부모 A와 자식 E, F로 갈 수 있음.
    #     "C": ["A", "G"],      # C에서 부모 A와 자식 G로 갈 수 있음.
    #     "D": ["A"],           # D에서 부모 A로 되돌아갈 수 있음.
    #     "E": ["B"],           # E에서 부모 B로 되돌아갈 수 있음.
    #     "F": ["B"],           # F에서 부모 B로 되돌아갈 수 있음.
    #     "G": ["C"],           # G에서 부모 C로 되돌아갈 수 있음.
    # }                          # 원래 graph와 달리 역방향 이동도 포함된 지도임.
    # 예: B.parents=["A"]를 읽으면 B의 이웃에 A를 넣고, A의 이웃에도 B를 넣음.
    # 즉, 원본 Commit.parents를 수정하지 않고 탐색용 연결만 별도로 만드는 것임.
    # 이웃은 path_step_key의 '해시 + ->' 값으로 정렬하며, 이 예시는 A~G 이름순과 같음.
    # Python의 사전·리스트 순서가 메모리 상태 때문에 무작위로 바뀌는 것은 아님.
    # 정렬은 커밋·부모의 등록 순서가 달라도 같은 연결에서 방문 순서를 일정하게 하려는 것임.
    # 이 나무에서는 B→D 경로가 하나뿐임. 여러 최단 경로가 있는 그래프에서는 동률 선택에도 쓰임.
    

    ready = deque([start_hash])  # 출발점부터 가까운 거리 순서로 방문함.
    # [5. 대기열과 발견 기록 초기화]
    # deque는 double-ended queue, 양쪽 끝에서 넣고 꺼낼 수 있는 큐임.
    # 여기서는 오른쪽에 넣는 append와 왼쪽에서 꺼내는 popleft를 사용함.
    # FIFO(First In, First Out), 먼저 넣은 항목을 먼저 처리하는 순서가 됨.
    # 현재 ready = deque(["B"]). 아직 처리할 곳은 출발점 B 하나뿐임.
    # 아래 설명에서는 deque 안의 내용을 간단히 [B, A]처럼 표시함. 실제 값은 문자열임.
    
    previous = {start_hash: None}  # 직전 번호와 방문 표시를 함께 기억함.
    # 현재 previous = {"B": None}. 출발점 B는 직전 위치가 없으므로 None임.
    # 키: 이미 발견하여 예약한 해시. 값: 그 해시를 처음 발견하게 해 준 직전 해시.
    # 예: previous["A"]="B"는 'B에서 A로 이동해서 A를 발견했다'는 뜻임.
    # 이 값은 Git의 부모를 뜻하지 않음! A의 Git 부모는 없지만 탐색상 직전 위치는 B임.
    # previous에 있으면 이미 예약됐거나 처리됐다는 뜻이지, 반드시 처리가 끝났다는 뜻은 아님.
    # 큐에서 꺼내기 전에 기록하므로 다른 이웃이 같은 노드를 발견해도 중복으로 예약하지 않음.
    
    while ready:  # 아직 확인할 커밋이 남아 있는 동안 반복함.
        current = ready.popleft()  # 현재 가장 가까운 후보를 꺼냄.
        # [6. while을 한 번 돌 때마다 한 노드를 꺼내 그 노드의 이웃을 확인함]
        # 아래 큐는 왼쪽이 다음에 꺼낼 위치임. '종료 시 큐'는 이웃 예약까지 마친 상태임.
        # 회차 | 꺼내기 전 ready | current | 새로 예약한 이웃 | 회차 종료 시 ready
        #  1   | [B]             | B       | A, E, F          | [A, E, F]
        #  2   | [A, E, F]       | A       | C, D             | [E, F, C, D]
        #  3   | [E, F, C, D]    | E       | 없음             | [F, C, D]
        #  4   | [F, C, D]       | F       | 없음             | [C, D]
        #  5   | [C, D]          | C       | G                | [D, G]
        #  6   | [D, G]          | D       | 확인하지 않음    | [G]인 상태에서 반환
        # 2회차에서 A를 꺼내도 E, F는 큐에 남음. 새 이웃 C, D는 그 뒤에 붙음.
        # 따라서 B에서 거리 1인 A, E, F를 모두 꺼낸 뒤 거리 2인 C, D를 꺼냄.
        # 거리 3인 G가 예약되어도 먼저 예약한 거리 2의 D보다 앞서 처리되지 않음.
    
        # [7. 현재 꺼낸 노드가 D이면 경로를 복원하고 함수 전체를 끝냄]
        # D는 2회차에 '발견되어 예약'되지만, 이 코드는 6회차에 D를 '꺼냈을 때' 반환함.
        # 이때 previous = {"B": None, "A": "B", "E": "B", "F": "B",
        #                  "C": "A", "D": "A", "G": "C"}임.
        # _restore_path는 D → previous["D"]인 A → previous["A"]인 B
        # → previous["B"]인 None 순서로 되짚어 ["D", "A", "B"]를 만든 뒤 뒤집음.
        # 최종 반환값은 ["B", "A", "D"]. 이동한 간선은 B-A, A-D 두 개임.
        # 실제 꺼낸 순서 B, A, E, F, C, D 전체를 반환하는 것이 아님!
        # E, F, C는 확인했어도 D로 이어진 직전 위치 사슬에 없으므로 결과에서 빠짐.
        # G는 큐에 남아 있지만 목적지의 최단 경로를 얻었으므로 처리할 필요가 없음.
        if current == end_hash:  
            return _restore_path(previous, end_hash)  # 저장해 둔 직전 번호로 경로를 복원함.
    
        # [8. 아직 목적지가 아니라면 current의 이웃 목록을 왼쪽부터 하나씩 확인함]
        for neighbor in neighbors[current]:               # dict[str, list[str]] 사전순으로 이웃을 확인함.
            # 첫 회차 current="B"이므로 neighbors[current]는 ["A", "E", "F"]임.
            # neighbor는 리스트 전체가 아니라 차례로 "A", "E", "F" 한 개씩 들어오는 변수임.
            # 두 번째 회차 current="A"에서는 ["B", "C", "D"]를 순서대로 확인함.
            # B는 이미 previous에 있으므로 건너뛰고 C, D만 새로 예약함.
            # E와 F의 유일한 이웃 B, C의 이웃 A도 이미 발견했으므로 다시 넣지 않음.
            if neighbor not in previous:        # 처음 발견한 경우에만 방문 예약함.
                previous[neighbor] = current    # 이웃으로 가기 직전의 번호를 기억함.
                # 첫 회차 A 발견: previous={"B": None, "A": "B"}가 됨.
                # 이어서 E 발견: "E": "B" 추가. F 발견: "F": "B" 추가.
                # 두 번째 회차 C 발견: "C": "A" 추가. D 발견: "D": "A" 추가.
                # 다섯 번째 회차 G 발견: "G": "C" 추가. 기존 키의 값을 덮어쓰지 않음.
                ready.append(neighbor)          # 이번에 발견한 이웃 하나를 기존 대기열의 맨 뒤에 예약함.
                # 첫 회차 큐 변화: [] → [A] → [A, E] → [A, E, F].
                # 두 번째 회차 큐 변화: [E, F] → [E, F, C] → [E, F, C, D].
                # append 한 번마다 while로 돌아가는 것이 아님. for의 다음 이웃을 확인함.
                # current의 이웃을 모두 확인하여 for가 끝난 뒤 다음 while 회차로 넘어감.

    # [9. 목적지를 꺼내지 못한 채 큐가 비었을 때만 이 줄에 도달함]
    # 이번 B→D 양방향 예시는 위에서 반환했으므로 여기까지 오지 않음.
    # 같은 commits에서 directed=True이면 부모 방향만 가능하므로 B→A까지만 이동함.
    # A.parents=[]라 더 갈 곳이 없고 D에는 도달하지 못하여 None을 반환함.
    # 이 함수는 출력하지 않음. 서비스와 출력 담당 코드가 None을 'No path'로 보여 줌.
    return None  # 모든 연결을 확인해도 목적지를 만나지 못했음.






# -------------------------------------------------------------------------------
# ✅ 🔥🔥🔥🔥🔥 ANCESTORS 명령어
# 부모 방향으로만 BFS를 진행해 모든 조상을 중복 없이 반환함.
def get_ancestors(commits: dict[str, Commit], start_hash: str) -> list[str]:
    
    """부모 방향으로 BFS를 끝까지 진행하여 모든 조상 해시를 모은다.

    입력은 커밋 사전과 대상 해시다.
    visited로 공통 조상의 중복을 막고 result에 발견 순서를 유지한다.
    정상 DAG(Directed Acyclic Graph, 방향성 비순환 그래프)에서
    대상 자신은 제외된다. 첫 부모만 찾고 중단하지 않는다.
    없는 대상은 빈 목록이고 존재하지 않는 부모 연결은 건너뛴다.
    순환 유효성 검사는 별도 책임이다. 방문한 부분의 시간은 O(Va+Ea)다.
    Va와 Ea는 대상에서 부모 방향으로 도달한 커밋과 연결 수다.
    """
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
