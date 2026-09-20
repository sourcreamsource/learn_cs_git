# 🟩 22_DAG (방향성 비순환 그래프) - 쉽게 이해하기  

> **한 줄 요약**: **화살표가 한 방향으로만 가고, 절대 되돌아오지 않는 그림**  
> **Git에서**: 커밋이 부모를 가리키는 구조 = DAG  

<br><br>

## 🟢 1. 이름 풀기  

| 용어 | 뜻 | 쉽게 |
|------|-----|------|
| **D**irected (방향성) | 화살표가 있음 (A → B) | 일방통행 도로 |
| **A**cyclic (비순환) | 순환(고리) 없음 | 다시 돌아올 수 없음 |
| **G**raph (그래프) | 점(노드)과 선(간선) | 점과 선으로 그린 그림 |

<br><br>

## 🟢 2. 비유: 가족 계보도 (족보)  

```
할아버지 ●
          ↓
      아버지 ●
          ↓
        나 ●
          ↓
       내 자식 ●
```

- **화살표 방향**: 부모 → 자식 (위에서 아래로)  
- **순환 없음**: 자식이 다시 부모가 될 수 없음  
- **여러 부모 가능**: 합가(입양) 등으로 부모가 2명일 수 있음 → **Merge Commit**  

> **이게 바로 DAG!**  

<br><br>

## 🟢 3. Git 커밋 그래프 = DAG  

### 🟡 일반적 상황 (한 줄 역사)  
```
C0 (첫 커밋) → C1 → C2 → C3 (최신)
```
- 각 커밋은 **부모 1개**  
- 화살표: **자식 → 부모** (Git은 거꾸로 가리킴!)  

### 🟡 브랜치 나눠진 상황  
```
        C3 ← C4 (feature 브랜치)
       /
C0 → C1 → C2 (main 브랜치)
       \
        C5 ← C6 (hotfix 브랜치)
```
- C2에서 **가지가 뻗어나감**  
- 각 커밋은 여전히 **부모를 가리킴** (화살표: 자식 → 부모)  

### 🟡 Merge 상황 (부모가 2개!)  
```
C0 → C1 → C2 → C3 → C5 (main)
           ↘     ↗
            C4 (feature)
```
- **C5의 부모가 2개**: C3 (main), C4 (feature)  
- **여전히 순환 없음** → DAG 유지  

<br><br>

## 🟢 4. 왜 Git은 DAG인가?  

### 🟡 1. 역사(히스토리)는 시간을 거스르지 않음  
- 과거 → 현재 → 미래 한 방향  
- **되돌아갈 수 없음** (시간 여행 불가)  

### 🟡 2. 커밋은 불변(Immutable)  
- 한번 만든 커밋은 **절대 안 바뀜**  
- 새 커밋은 **기존 커밋을 부모로 가리킴**  
- 기존 커밋이 새 커밋을 알 필요 없음 (단방향)  

### 🟡 3. 분산 환경에서 합치기 쉬움  
- 각자 작업하다가 **공통 조상** 찾아서 합치면 됨  
- 순환 없으니 **충돌 계산이 명확**  

<br><br>

## 🟢 5. DAG vs 일반 그래프 vs 트리  

| 구조 | 특징 | 예시 |
|------|------|------|
| **트리 (Tree)** | 부모 1개, 순환 없음 | 폴더 구조, 조직도 |
| **DAG** | 부모 여러 개 가능, 순환 없음 | **Git 커밋**, 작업 의존성, 패키지 의존성 |
| **일반 그래프** | 순환 가능 | 지도(도로망), SNS 친구 관계 |

### 🟡 그림으로 비교  
```
트리:           DAG:              일반 그래프:
  A               A                   A
 / \             / \                 / \
B   C           B   C               B   C
                \ /                 \ /
                 D                   D ←──┐
                                        │  │
                                        └──┘ (순환!)
```

<br><br>

## 🟢 6. Mini Git에서 DAG 표현하기  

### 🟡 커밋 노드 클래스  
```python
class Commit:
    def __init__(self, hash_val, message, author, timestamp, parents):
        self.hash = hash_val          # 고유 ID
        self.message = message        # 커밋 메시지
        self.author = author          # 작성자
        self.timestamp = timestamp    # 시간
        self.parents = parents        # 부모 해시 리스트 [] 또는 [parent1, parent2]
```

### 🟡 저장소: 해시맵으로 모든 커밋 저장  
```python
class Repository:
    def __init__(self):
        self.commits = {}  # {hash: Commit객체}
        self.branches = {} # {브랜치명: 커밋해시}
        self.head = None   # 현재 브랜치명
```

### 🟡 DAG 순회 예시: 조상 찾기 (ANCESTORS)  
```python
def get_ancestors(self, commit_hash):
    """해당 커밋의 모든 조상 찾기 (DFS/BFS)"""
    visited = set()
    ancestors = []
    
    def dfs(hash_val):
        if hash_val in visited:
            return
        visited.add(hash_val)
        commit = self.commits[hash_val]
        for parent_hash in commit.parents:
            ancestors.append(parent_hash)
            dfs(parent_hash)  # 재귀적으로 부모의 부모도
    
    dfs(commit_hash)
    return ancestors
```

<br><br>

## 🟢 7. DAG에서 중요한 연산들  

| 연산 | 설명 | Mini Git 명령어 |
|------|------|-----------------|
| **위상 정렬** | 부모가 자식보다 먼저 오게 줄 세우기 | `LOG` |
| **최단 경로** | 두 노드 사이 최소 간선 수 경로 | `PATH` |
| **모든 조상** | 도달 가능한 모든 부모/조부모 찾기 | `ANCESTORS` |
| **공통 조상** | 두 노드의 공통 부모 중 가장 가까운 것 | Merge 시 필요 (LCA) |
| **도달 가능성** | A에서 B로 갈 수 있나? | 브랜치 포함 여부 확인 |

<br><br>

## 🟢 8. 핵심 포인트 정리  

### 🟡 1. 화살표 방향 주의!  
- **Git 저장 방식**: 자식 → 부모 (뒤로 가리킴)  
- **시간 흐름**: 부모 → 자식 (앞으로 감)  
- **LOG 출력 순서**: 부모 → 자식 (위상 정렬)  

### 🟡 2. Merge Commit = 부모 2개  
```python
# Merge 시 부모가 2개
merge_commit = Commit(
    hash="m1e2r3",
    message="Merge branch 'feature'",
    author="홍길동",
    timestamp=now(),
    parents=["main_tip_hash", "feature_tip_hash"]  # 부모 2개!
)
```

### 🟡 3. 순환 검사 (안전장치)  
```python
def would_create_cycle(child_hash, parent_hash):
    """child의 조상에 parent가 있으면 순환 발생!"""
    ancestors = get_ancestors(child_hash)
    return parent_hash in ancestors
```
> Git은 이 검사 안 해도 됨 (사용자가 실수로 순환 만들 수 없음)  

<br><br>

## 🟢 9. 미니 실습: 종이로 그려보기  

### 🟡 상황  
```
1. init "홍길동"          → C0 (main)
2. commit "첫 화면"       → C1 (parent: C0)
3. branch feature         → feature 브랜치 = C1
4. switch feature         → HEAD = feature
5. commit "로그인 추가"    → C2 (parent: C1)
6. commit "로그인 완료"    → C3 (parent: C2)
7. switch main            → HEAD = main
8. commit "회원가입 추가"  → C4 (parent: C1)
9. merge feature          → C5 (parents: C4, C3)
```

### 🟡 그려보기 (화살표: 자식 → 부모)  
```
C0 ← C1 ← C2 ← C3
         ↘     ↗
           C4 ← C5 (merge)
           
main:    C0 → C1 → C4 → C5
feature: C0 → C1 → C2 → C3
```

<br><br>

## 🟢 10. 더 알아보기 (심화)  

| 주제 | 설명 |
|------|------|
| **LCA (Lowest Common Ancestor)** | 두 노드의 가장 가까운 공통 조상 - Merge base 찾기용 |
| **DAG 위의 DP** | DAG에서 최장 경로, 경로 개수 세기 등 동적계획법 가능 |
| **Git 내부** | `.git/objects/`에 커밋 객체 저장, 해시로 주소 지정 |
| **Garbage Collection** | 어떤 브랜치에서도 도달 못 하는 커밋 = 쓰레기 (gc로 삭제) |

<br><br>

---

## 🟩 요약: 시험/면접용 한 줄 암기  

> **DAG (Directed Acyclic Graph)** = **방향성 있는 비순환 그래프**  
> **Git 커밋 그래프 = DAG** (자식→부모 화살표, 순환 없음, 부모 여러 개 가능)  
> **핵심 연산**: 위상 정렬(LOG), BFS(PATH/ANCESTORS), LCA(Merge base)  

<br><br>