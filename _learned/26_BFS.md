# 🟩 26_BFS (너비 우선 탐색) - 쉽게 이해하기  

> **한 줄 요약**: **시작점에서 가까운 곳부터 동그랗게 퍼지며 탐색**  
> **Mini Git에서**: `PATH`(최단 경로), `ANCESTORS`(모든 조상) 구현에 필수!  

<br><br>

## 🟢 1. 비유: 물웅덩이에 돌 던지기  

```
던진 지점 (시작)
     │
  ┌──┼──┐
  │  │  │   ← 1단계: 바로 옆 (거리 1)
┌─┴┐ │ ┌─┴┐
│  │ │ │  │   ← 2단계: 그 옆 (거리 2)
...
```
- **파문(물결)이 퍼지듯** 가까운 곳부터 차례차례 방문  
- **최단 거리**를 자연스럽게 찾게 됨  

<br><br>

## 🟢 2. BFS vs DFS 비교  

| | **BFS (너비 우선)** | **DFS (깊이 우선)** |
|---|---------------------|---------------------|
| **자료구조** | **큐 (Queue)** - FIFO | **스택 (Stack)** - LIFO (또는 재귀) |
| **탐색 순서** | 가까운 곳부터 | 깊숙한 곳부터 |
| **최단 경로** | ✅ 보장 | ❌ 보장 안 됨 |
| **메모리** | 넓으면 많이 씀 | 깊으면 많이 씀 |
| **구현** | `collections.deque` | 재귀 또는 리스트 `append/pop` |

### 🟡 그림으로 보기  
```
그래프:     A
           / \
          B   C
         /   / \
        D   E   F

BFS 순서: A → B → C → D → E → F  (레벨별)
DFS 순서: A → B → D → C → E → F  (깊게 파고듦)
```

<br><br>

## 🟢 3. BFS 기본 템플릿 (외우지 말고 이해하세요!)  

```python
from collections import deque

def bfs_basic(graph, start):
    """
    graph: {노드: [이웃노드들]} 인접 리스트
    start: 시작 노드
    """
    visited = set()        # 방문 체크 (중복 방지)
    queue = deque([start]) # 큐에 시작점 넣기
    visited.add(start)
    
    while queue:           # 큐가 빌 때까지
        node = queue.popleft()  # 앞에서 꺼내기 (FIFO)
        print(f"방문: {node}")   # 여기서 할 일 하기
        
        for neighbor in graph[node]:  # 이웃들 확인
            if neighbor not in visited:
                visited.add(neighbor)  # 방문 표시
                queue.append(neighbor) # 뒤에 넣기
```

> **핵심 3줄**: `popleft()` → `for neighbor` → `append()`  

<br><br>

## 🟢 4. Mini Git 활용 1: 최단 경로 (PATH 명령)  

### 🟡 문제: 두 커밋 사이 최단 경로 찾기  
- **무방향 그래프**로 취급 (부모→자식, 자식→양방향)  
- **간선 가중치 모두 1** → BFS가 최단 경로 보장!  
- **여러 최단 경로면**: 해시 문자열 연결했을 때 **사전순 최소** 선택  

### 🟡 구현: 경로 추적용 parent 딕셔너리 추가  
```python
def find_shortest_path(graph, start, end):
    """
    graph: 무방향 인접 리스트 {노드: [이웃들]}
    return: [start, ..., end] 경로 리스트, 없으면 None
    """
    if start == end:
        return [start]
    
    visited = set([start])
    queue = deque([start])
    parent = {start: None}  # 경로 복원용: 자식 → 부모 매핑
    
    while queue:
        node = queue.popleft()
        
        # 이웃 정렬: 사전순으로 먼저 탐색되게 (tie-break용)
        for neighbor in sorted(graph[node]):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = node  # "neighbor의 부모는 node"
                queue.append(neighbor)
                
                if neighbor == end:  # 도착!
                    # 경로 복원 (거꾸로 올라가기)
                    path = []
                    curr = end
                    while curr is not None:
                        path.append(curr)
                        curr = parent[curr]
                    return path[::-1]  # 뒤집어서 start→end 순서로
    
    return None  # 경로 없음
```

### 🟡 무방향 그래프 만들기 (Git 커밋 그래프 → 무방향)  
```python
def build_undirected_graph(commits):
    """커밋 그래프(자식→부모)를 무방향으로 변환"""
    graph = {hash_val: [] for hash_val in commits}
    
    for hash_val, commit in commits.items():
        for parent_hash in commit.parents:
            # 양방향 연결
            graph[hash_val].append(parent_hash)
            graph[parent_hash].append(hash_val)
    
    return graph

# 사용 예
undirected = build_undirected_graph(repo.commits)
path = find_shortest_path(undirected, "C0", "C5")
# ['C0', 'C1', 'C4', 'C5'] 또는 ['C0', 'C1', 'C2', 'C3', 'C5']
# → 더 짧은 것(길이 4) 선택, 같으면 사전순 비교
```

<br><br>

## 🟢 5. Mini Git 활용 2: 모든 조상 찾기 (ANCESTORS 명령)  

### 🟡 문제: 특정 커밋에서 도달 가능한 모든 조상 출력  
- **방향 그래프** 유지 (자식 → 부모 방향만 따라감)  
- **BFS 또는 DFS 둘 다 가능** (최단 경로 필요 없으니까)  
- 방문 체크 필수 (같은 조상 중복 방문 방지)  

### 🟡 BFS 구현  
```python
def get_all_ancestors_bfs(commits, start_hash):
    """
    commits: {hash: Commit객체} - Commit.parents 리스트 있음
    return: 조상 해시 리스트 (순서 무관)
    """
    visited = set()
    queue = deque([start_hash])
    ancestors = []
    
    while queue:
        current = queue.popleft()
        
        # 부모들 방문
        for parent_hash in commits[current].parents:
            if parent_hash not in visited:
                visited.add(parent_hash)
                ancestors.append(parent_hash)
                queue.append(parent_hash)
    
    return ancestors
```

### 🟡 DFS 구현 (더 간단)  
```python
def get_all_ancestors_dfs(commits, start_hash):
    visited = set()
    ancestors = []
    
    def dfs(hash_val):
        for parent_hash in commits[hash_val].parents:
            if parent_hash not in visited:
                visited.add(parent_hash)
                ancestors.append(parent_hash)
                dfs(parent_hash)
    
    dfs(start_hash)
    return ancestors
```

<br><br>

## 🟢 6. 시간/공간 복잡도  

| 연산 | 시간 | 공간 |
|------|------|------|
| **BFS 기본** | O(V + E) | O(V) |
| **최단 경로 (PATH)** | O(V + E) | O(V) - parent 딕셔너리 |
| **모든 조상 (ANCESTORS)** | O(V + E) | O(V) - visited 집합 |

> **V = 커밋 수, E = 부모-자식 관계 수**  
> Git 저장소 크기가 커도 **선형 시간이라 빠름**  

<br><br>

## 🟢 7. 핵심 포인트 & 실수 방지  

### 🟡 1. `deque` 써야 빠름!  
```python
# ❌ 느림: 리스트 pop(0)은 O(N)
queue = [start]
node = queue.pop(0)

# ✅ 빠름: deque popleft()는 O(1)
from collections import deque
queue = deque([start])
node = queue.popleft()
```

### 🟡 2. 방문 체크는 **큐에 넣을 때** 바로!  
```python
# ❌ 틀림: 꺼낼 때 체크 → 중복 들어감
if neighbor not in visited:
    queue.append(neighbor)

# ✅ 맞음: 넣을 때 체크 → 중복 방지
if neighbor not in visited:
    visited.add(neighbor)
    queue.append(neighbor)
```

### 🟡 3. PATH에서 사전순 타이브레이크  
```python
# 이웃을 정렬해서 탐색하면 첫 발견 경로가 사전순 최소!
for neighbor in sorted(graph[node]):  # ← 이거 중요!
    ...
```

### 🟡 4. 무방향 vs 유방향 구별  
| 명령 | 그래프 종류 | 방향 |
|------|-------------|------|
| `PATH` | **무방향** | 부모↔자식 양방향 |
| `ANCESTORS` | **유방향** | 자식→부모만 |
| `LOG` (위상정렬) | **유방향** | 부모→자식 |

<br><br>

## 🟢 8. 미니 실습: 직접 돌려보기  

```python
from collections import deque

# 무방향 그래프 예시
graph = {
    'A': ['B', 'C'],
    'B': ['A', 'D'],
    'C': ['A', 'E', 'F'],
    'D': ['B'],
    'E': ['C'],
    'F': ['C']
}

# BFS 기본 순서
def bfs_order(graph, start):
    visited = set([start])
    q = deque([start])
    order = []
    while q:
        n = q.popleft()
        order.append(n)
        for neigh in sorted(graph[n]):  # 정렬해서 일관된 순서
            if neigh not in visited:
                visited.add(neigh)
                q.append(neigh)
    return order

print("BFS 순서:", bfs_order(graph, 'A'))
# ['A', 'B', 'C', 'D', 'E', 'F']

# 최단 경로
print("A→D 최단:", find_shortest_path(graph, 'A', 'D'))
# ['A', 'B', 'D']

print("A→F 최단:", find_shortest_path(graph, 'A', 'F'))
# ['A', 'C', 'F']
```

<br><br>

## 🟢 9. 더 알아보기 (심화)  

| 주제 | 설명 |
|------|------|
| **양방향 BFS** | 시작/끝에서 동시에 탐색 → 2배 빠름 (거대 그래프용) |
| **0-1 BFS** | 가중치 0, 1인 그래프 최단 경로 (데크 사용) |
| **다익스트라** | 가중치 양수인 그래프 최단 경로 (우선순위 큐) |
| **A* 알고리즘** | 휴리스틱 이용해 더 빠른 경로 탐색 (게임, 네비) |

<br><br>

---

## 🟩 요약: 시험/면접용 한 줄 암기  

> **BFS** = **큐(Queue)**로 **가까운 곳부터** 탐색  
> **최단 경로 보장** (가중치 없는 그래프)  
> **구현 핵심**: `popleft()` → 이웃 순회 → `append()` + `visited` 체크  
> **Mini Git**: `PATH`(무방향 BFS + parent 복원), `ANCESTORS`(유방향 BFS/DFS)  

<br><br>