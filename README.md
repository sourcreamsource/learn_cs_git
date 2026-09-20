# 🟩 Mini Git

Python으로 커밋·브랜치·검색·그래프 탐색을 직접 구현한 학습용 명령줄 프로그램이다.

실제 Git을 대체하는 도구는 아니다. 커밋에는 **해시, 메시지, 작성자, 시각, 부모 해시**를 저장하며, 작업 파일의 내용을 저장하거나 복원하지 않는다. 데이터는 메모리에만 있으므로 **프로그램을 종료하면 사라진다.**

## 🟢 시작 전에 알아둘 것

| 항목 | 내용 |
| --- | --- |
| Python | 3.10 이상. `pyproject.toml`에 조건이 지정되어 있다 |
| 환경 관리 | uv로 프로젝트 전용 Python 환경을 준비한다 |
| 외부 Python 패키지 | 없음. 현재는 표준 라이브러리만 사용한다 |
| 네트워크 | uv·Python·Docker 이미지 설치에는 필요할 수 있다. 앱의 기본 기능은 로컬에서 실행된다 |
| 초기화 | 앱 안에서 유효한 `INIT`을 다시 실행하면 기존 커밋·브랜치·색인이 초기화된다 |
| 파일 접근 | `COMMIT`은 파일을 읽지 않는다. `DIFF`는 지정한 두 텍스트 파일을 읽는다 |
| 계정·인증 | API(Application Programming Interface) 키, 외부 계정, 환경 파일 설정이 필요하지 않다 |

읽는 순서: **환경 구축 → 실행 → 첫 실습 → 명령어 → 구조와 코드 읽기 → 테스트 → 선택적 Docker 실습**.

<br><br>

## 🟢 1. uv 환경 구축

### 🟡 1-1. 프로젝트 폴더에서 터미널 열기

편집기로 이 프로젝트를 열고 터미널을 실행한다. `README.md`, `pyproject.toml`, `uv.lock`, `git-app`이 보이는 최상위 폴더에서 아래 명령을 실행한다.

```bash
# 현재 폴더의 파일과 하위 폴더 이름을 확인한다.
ls
```

`ls`는 list, 목록을 보여 주는 명령이다. 이미 받은 프로젝트이므로 `uv init`으로 새 프로젝트를 만들 필요는 없다.

### 🟡 1-2. uv 설치하기

먼저 설치 여부를 확인한다.

```bash
# uv가 설치되어 있으면 버전 번호가 나온다.
uv --version
```

버전이 나오면 다음 단계로 이동한다. `command not found: uv`라면 아래 두 방법 중 하나만 사용한다.

| 환경 | 설치 방법 |
| --- | --- |
| macOS에서 Homebrew를 이미 사용 중 | 아래 `brew install uv` 실행 |
| Homebrew가 없는 macOS 또는 Linux | 아래 공식 설치 스크립트 사용 |

```bash
# Homebrew가 설치된 환경에서 uv를 설치한다.
brew install uv
```

또는 공식 설치 스크립트를 사용한다. 이 명령은 인터넷에서 받은 스크립트를 실행하므로 공식 주소를 확인한 후 사용한다.

```bash
# 공식 uv 설치 스크립트를 다운로드하여 셸로 실행한다.
curl -LsSf https://astral.sh/uv/install.sh | sh
```

설치가 끝나면 터미널을 새로 열고 `uv --version`으로 다시 확인한다. 설치 방법은 [uv 공식 설치 문서](https://docs.astral.sh/uv/getting-started/installation/)를 기준으로 한다.

| 명령·옵션 | 의미 |
| --- | --- |
| `uv` | Python 프로젝트·환경 관리 도구 이름. 여기서는 약어를 임의로 풀어 쓰지 않는다 |
| `--version` | 설치된 버전 표시 |
| `brew install` | Homebrew 패키지 관리자로 도구 설치 |
| `curl` | URL(Uniform Resource Locator, 자원 주소)을 통해 데이터를 주고받는 도구 |
| `-L` | location: 다른 주소로 연결되면 따라감 |
| `-s` | silent: 진행 표시 숨김 |
| `-S` | show-error: silent 상태에서도 오류 표시 |
| `-f` | fail: HTTP(Hypertext Transfer Protocol, 웹 데이터 전송 규약) 오류 응답이면 실패 처리 |
| `\|` | 앞 명령의 출력을 뒤 명령의 입력으로 전달하는 파이프 |
| `sh` | shell: 전달받은 설치 스크립트를 실행하는 셸 |

### 🟡 1-3. 프로젝트 전용 환경 준비하기

```bash
# 잠금 파일을 바꾸지 않고 프로젝트 전용 환경을 준비한다.
uv sync --locked
# 프로젝트 환경이 사용하는 Python 버전을 확인한다.
uv run --locked python --version
```

`sync`는 synchronize, 환경을 프로젝트 설정에 맞추는 작업이다. `.venv`가 없으면 만들고, 필요한 Python이 없다면 다운로드할 수 있다. `--locked`는 기존 `uv.lock`의 변경을 허용하지 않는 옵션이다.

| 파일·폴더 | 역할 |
| --- | --- |
| `pyproject.toml` | 프로젝트 이름, 허용 Python 버전, 의존성 선언 |
| `uv.lock` | uv가 해석한 프로젝트와 의존성 정보를 기록하는 잠금 파일 |
| `.venv/` | virtual environment, 이 프로젝트 전용 실행 환경. Git에 올리지 않는다 |

현재 의존성 목록은 비어 있으므로 별도의 패키지 설치 목록은 없다. `uv run`이 프로젝트 환경을 사용하므로 가상환경을 따로 활성화하지 않아도 된다. `uv sync`는 전용 환경을 선언된 의존성에 맞추므로 `.venv`를 다른 프로젝트와 공유하지 않는다. [uv 프로젝트 사용 안내](https://docs.astral.sh/uv/guides/projects/)

<br><br>

## 🟢 2. 프로그램 실행과 종료

### 🟡 터미널에서 실행

```bash
# 프로젝트 환경에서 git-app 패키지의 실행 시작점을 호출한다.
uv run --locked python -m git-app
```

| 부분 | 의미 |
| --- | --- |
| `run` | 프로젝트 환경에서 뒤의 명령 실행 |
| `python` | Python 실행기 |
| `-m` | module: 지정한 모듈·패키지를 실행 |
| `git-app` | 실행할 패키지 이름. `git-app/__main__.py`가 시작점 |

환영 문구와 `mini-git>`가 나오면 실행된 것이다. 이제부터 `INIT`, `LOG` 같은 앱 명령은 **이 입력창에** 넣는다. 터미널의 일반 셸에 입력하는 명령이 아니다.

CLI는 Command Line Interface, 명령줄 인터페이스다. 이 프로그램은 REPL(Read-Eval-Print Loop, 읽기·실행·출력·반복) 방식으로 한 줄씩 입력을 받는다.

### 🟡 앱 안에서 종료

```text
EXIT
```

`QUIT`도 같은 기능이다. `Ctrl+C` 또는 `Ctrl+D`로도 종료할 수 있다. 종료 후 다시 실행하면 빈 상태에서 시작하므로 다시 `INIT`이 필요하다.

이미 Python 3.10 이상이 준비된 환경에서는 `python3 -m git-app`으로 직접 실행할 수도 있다. 다만 프로젝트 환경을 일관되게 사용하려면 위의 uv 명령을 사용한다.

<br><br>

## 🟢 3. 처음부터 따라 하는 실습

### 🟡 3-1. 기록 생성 → 가지 분리 → 병합 → 조회

앱의 `mini-git>` 입력창에서 아래 내용을 한 줄씩 실행한다. `mini-git>` 표시 자체는 입력하지 않는다.

```text
INIT "Alice Example"
COMMIT "Initial project"
BRANCH feature
SWITCH feature
COMMIT "Add login feature"
SWITCH main
COMMIT "Add payment feature"
MERGE feature
BRANCH LIST
LOG
SEARCH "login feature"
SEARCH --author="alice example"
LOG --sort-by=date
LOG --sort-by=author
```

| 입력 단계 | 일어나는 일 |
| --- | --- |
| `INIT` | main 브랜치와 작성자를 설정하고 HEAD가 main을 가리키게 한다 |
| 첫 `COMMIT` | 부모가 없는 첫 커밋을 만든다 |
| `BRANCH feature` | 같은 커밋을 가리키는 새 이름표를 만든다. 자동 전환하지는 않는다 |
| `SWITCH feature` 뒤 `COMMIT` | feature의 최신 커밋을 앞으로 이동한다. main은 그대로다 |
| `SWITCH main` 뒤 `COMMIT` | main에도 별도의 다음 커밋을 만든다 |
| `MERGE feature` | main·feature의 최신 커밋을 부모로 갖는 새 커밋을 main에 만든다 |
| `BRANCH LIST` | 두 브랜치를 표시한다. 현재 브랜치 main에 `*`가 붙는다 |
| `LOG` | 전체 커밋 4개를 부모가 먼저 나오도록 보여 준다 |
| 두 `SEARCH` | 단어 검색은 1개, 작성자 검색은 4개의 커밋을 찾는다 |
| 정렬 옵션이 있는 `LOG` | 날짜 또는 작성자 기준으로 보여 준다. 이 예시는 작성자가 모두 같아 이름순 차이가 드러나지 않는다 |

`MERGE`는 커밋 관계를 합치는 기능이다. 실제 파일 내용 병합, 충돌 해결, 작업 폴더 변경은 수행하지 않는다.

### 🟡 3-2. 실제 해시로 경로와 조상 찾기

커밋 생성 시 `[main a1b2c3]` 같은 표시가 나온다. `a1b2c3` 부분이 커밋 해시, 즉 기록을 구분하는 번호다. 기본 번호는 실행마다 달라질 수 있으므로 예시 번호를 그대로 쓰지 않는다.

1. `LOG`에서 `Initial project`의 해시와 마지막 병합 커밋의 해시를 확인한다.
2. `PATH`만 입력한다. 질문이 나오면 첫 커밋 해시, 병합 커밋 해시 순서로 입력한다.
3. `Path: ...`로 가장 짧은 경로 하나가 나온다.
4. `ANCESTORS`만 입력한 뒤 병합 커밋의 해시를 넣는다. 앞서 만든 커밋 3개가 중복 없이 나온다.

PATH는 Breadth-First Search(BFS, 너비 우선 탐색)를 사용한다. 가까운 커밋부터 확인하므로 간선 개수가 가장 적은 경로를 찾는다.

### 🟡 3-3. 입력 방식

| 방식 | 예시 | 동작 |
| --- | --- | --- |
| 한 줄 입력 | `COMMIT "Add login"` | 메시지를 받아 바로 실행 |
| 대화형 입력 | `COMMIT` | 메시지를 질문 |
| 일부 생략 | `PATH 실제시작해시` | 빠진 도착 해시를 질문 |

명령 이름은 대소문자를 구분하지 않는다. 브랜치 이름과 해시는 입력한 문자열을 사용한다. 공백이 있는 이름·메시지·검색어는 따옴표로 묶는다. 메시지가 `--`로 시작하면 `COMMIT -- "--설명"`처럼 옵션 해석 종료 표시를 넣는다.

<br><br>

## 🟢 4. 지원 명령어

아래의 `<이름>`, `<해시>`는 실제 값으로 바꾸는 자리다. 꺾쇠까지 입력하지 않는다.

| 명령 | 기능과 주의점 |
| --- | --- |
| `INIT <사용자이름>` | initialize, 초기화. 유효한 이름이면 기존 상태를 비우고 main·HEAD·작성자 설정 |
| `BRANCH <브랜치이름>` | 현재 커밋을 가리키는 가지 생성. 커밋을 복사하지 않음 |
| `BRANCH LIST` | 가지 목록 조회. `*`는 현재 가지. LIST는 조회용 예약어 |
| `SWITCH <브랜치이름>` | 현재 브랜치 전환 |
| `COMMIT "메시지"` | 현재 브랜치의 최신 커밋을 부모로 새 기록 생성 |
| `LOG` | 모든 브랜치의 기록을 부모 우선으로 출력 |
| `LOG --sort-by=date` | 시각 오름차순. 같은 값이면 저장 순서 유지 |
| `LOG --sort-by=author` | 소문자로 비교한 작성자 이름순. 부모 우선 보장과는 별개 |
| `PATH <시작해시> <도착해시>` | 부모·자식 양쪽으로 이동하는 최단 경로 |
| `PATH <시작해시> <도착해시> --directed` | 자식에서 부모 방향으로만 이동. `--directed=false`는 양방향 |
| `ANCESTORS <해시>` | 모든 조상을 중복 없이 발견 순서로 출력 |
| `SEARCH "단어"` | 메시지의 소문자 단어와 정확히 일치하는 커밋 검색 |
| `SEARCH "단어1 단어2"` | 두 단어가 모두 있는 커밋 검색. 연속된 문장인지 검사하지 않음 |
| `SEARCH --author="작성자 이름"` | 앞뒤 공백·대소문자를 정리한 작성자 전체 이름으로 검색 |
| `MERGE <대상브랜치>` | 현재 가지에 부모 둘을 가진 병합 커밋 생성. 두 가지 모두 커밋 필요 |
| `DIFF <파일1> <파일2>` | difference, 차이 비교. 두 UTF-8(Unicode Transformation Format의 8비트 인코딩 방식) 텍스트 파일의 줄 비교 |
| `BENCH` | benchmark, 성능 측정. 입력 100·500·1000·3000개로 두 정렬 시간 비교 |
| `HELP` | 도움말 |
| `EXIT`, `QUIT` | 프로그램 종료 |

- `SEARCH login`은 `login,`이나 `logging`을 찾지 않는다. 공백으로 나눈 단어를 비교하며 문장부호를 제거하지 않는다.
- PATH가 여러 개면 `hash1->hash2->...` 문자열의 사전순으로 하나를 고른다.
- 해시는 존재하지만 연결이 없으면 `No path`, 해시 자체가 없으면 `Unknown commit`이다.
- `DIFF`는 첫 파일에만 있는 줄을 `-`, 두 번째에만 있는 줄을 `+`, 공통 줄을 공백으로 표시한다. 상대 경로의 기준은 앱을 실행한 폴더다.
- `HELP`, `DIFF`, `BENCH`, 종료 명령은 저장소 초기화 없이 사용할 수 있다.
- `SEARCH --author`처럼 값이 필요한 옵션의 값을 생략하면 오류다.

<br><br>

## 🟢 5. 모듈 구조와 책임

### 🟡 실행 흐름

```text
git-app/__main__.py
    → bootstrap.create_app(): 저장소·색인·서비스를 만들고 연결
    → HybridCLI.start_repl(): 사용자 입력 반복
    → CommandParser.parse_line(): 명령·인자·옵션 분리
    → CommandDispatcher.dispatch(): 문법 검사와 담당자 선택
    → RepositoryCommands / HistoryCommands / BonusCommands
    → 서비스: 작업 조건과 실행 순서 결정
    → 저장소·색인·알고리즘: 보관하거나 계산
    → 명령 담당자·presenter: 결과를 화면에 출력
```

### 🟡 폴더별 역할

| 위치 | 대표 파일·클래스 | 맡는 일 |
| --- | --- | --- |
| `git-app/__init__.py` | 패키지 초기화 | 내부 모듈을 찾도록 Python 검색 경로 준비 |
| `git-app/__main__.py` | `main` | 앱을 만들고 입력 반복 시작 |
| `git-app/bootstrap.py` | `create_app` | 같은 저장소·색인·해시 생성기를 필요한 서비스에 연결 |
| `git-app/cli/` | `parser.py`, `commands.py`, `interactive.py`, `presenter.py` | 입력 해석, 명령 전달, 추가 질문, 화면 출력 |
| `git-app/services/` | `GitService`, `GraphService`, `SearchService`, `BonusService` | 기능별 조건 검사와 처리 조율 |
| `git-app/services/commit_writer.py` | `CommitWriter` | 일반·병합 커밋의 저장 → 브랜치 변경 → 색인 등록 절차 공유 |
| `git-app/repositories/` | `CommitRepository`, `BranchRepository` | 해시별 커밋과 브랜치·HEAD·작성자 상태 보관 |
| `git-app/models/commit.py` | `Commit` | 커밋 한 개의 다섯 필드 정의 |
| `git-app/graph/` | `topological_sort.py`, `paths.py`, `traversal.py` | 위상 정렬, 최단 경로·조상 탐색, 공통 호출 창구 |
| `git-app/index/inverted_index.py` | `InvertedIndex` | 단어·작성자에서 커밋 해시를 찾는 역색인 |
| `git-app/sort/` | `merge_sort.py`, `quick_sort.py` | 직접 구현한 병합 정렬과 퀵 정렬 |
| `git-app/validators/` | 입력·명령·파일·DAG 검사 | 잘못된 인자, 민감 파일명, 불완전하거나 순환하는 그래프 검사 |
| `git-app/utils/hash_generator.py` | `HashGenerator` | 해시 후보 생성과 세션 내 중복 검사 |
| `git-app/constants/` | `help_text.py`, `messages.py`, `git_constants.py` | 도움말·메시지·기본값 |
| `git-app/bonus/` | `diff.py`, `benchmark.py` | 줄 단위 차이 계산과 정렬 시간 측정 |
| `tests/` | `test_*.py` | 단위 테스트와 회귀 테스트 |

HEAD는 현재 선택한 브랜치 이름이다. 브랜치는 최신 커밋 해시를 가리키는 이름표이며, 커밋 본문은 `CommitRepository`에 따로 보관한다.

### 🟡 실제 코드를 어디서부터 읽을까?

한 기능을 골라 아래 순서로 따라간다. 각 함수의 docstring으로 입력과 결과를 먼저 읽고, 내부 주석과 실행문을 확인한다.

| 궁금한 기능 | 파일·함수를 읽는 순서 | 확인할 핵심 |
| --- | --- | --- |
| INIT | `cli/repository_commands.py`의 `handle_init` → `services/git_service.py`의 `init_repository` → `BranchRepository.initialize` | 이름 검사 뒤 초기화하는 이유 |
| COMMIT | `handle_commit` → `GitService.create_commit` → `CommitWriter.create` → `CommitRepository.save`·`InvertedIndex.add_commit` | 부모 결정과 저장·색인 갱신 순서 |
| LOG | `cli/history_commands.py`의 `handle_log` → `GraphService.get_topological_log` → `graph/topological_sort.py`의 `topological_sort` | 부모 처리가 끝난 자식만 출력 후보에 넣는 과정 |
| PATH | `handle_path` → `GraphService.get_shortest_path` → `graph/paths.py`의 `bfs_shortest_path` → `_restore_path` | 방문 표시, 직전 해시 저장, 경로 복원 |
| ANCESTORS | `handle_ancestors` → `GraphService.get_ancestors` → `graph/paths.py`의 `get_ancestors` | 부모 방향으로 끝까지 탐색하고 중복 제거 |
| SEARCH | `handle_search` → `SearchService` → `InvertedIndex` → `SearchService._find_commits` | 전체 커밋 대신 색인의 후보만 조회 |
| 정렬 LOG | `handle_log` → `SearchService.get_sorted_log` → `sort/merge_sort.py`의 `merge_sort` | 날짜·작성자 비교 기준과 안정 정렬 |
| MERGE | `cli/bonus_commands.py`의 `handle_merge` → `BonusService.merge_branch` → `CommitWriter.create` | 부모 두 개와 현재 브랜치만 갱신하는 흐름 |

위 표의 짧은 파일 경로는 모두 `git-app/` 아래를 기준으로 한다. `GraphTraversal`은 알고리즘을 연결하는 창구이고, `graph/dag.py`는 기존 경로에서도 `DAGValidator`를 가져올 수 있게 연결하는 파일이다.

<br><br>

## 🟢 6. 자료구조와 알고리즘

| 기능 | 구현 방식 | 성질·비용 |
| --- | --- | --- |
| 커밋 조회 | `dict[해시, Commit]` | 단건 조회 평균 O(1). 중복 저장은 별도로 거부 |
| 기본 LOG | Kahn 위상 정렬, `deque` | 알고리즘 시간 O(V+E). 부모가 자식보다 먼저 나옴 |
| PATH | 정렬된 이웃 목록 + BFS | 탐색 O(V+E)에 이웃 목록 정렬 비용이 추가됨 |
| ANCESTORS | 부모 방향 BFS + `set` | 도달 가능한 조상을 중복 없이 탐색 |
| 역색인 | `{단어 또는 작성자: {해시: None}}` | 검색 입구 조회 평균 O(1), 결과 K개를 꺼내는 비용 O(K). 다중 단어는 후보 교집합 검사 추가 |
| 병합 정렬 | 반으로 분할하고 안정 병합 | 평균·최악 O(N log N) |
| 퀵 정렬 | 작은 값·같은 값·큰 값 그룹과 작업 스택 | 평균 O(N log N), 최악 O(N²). 이 구현은 동점 순서를 유지 |
| DIFF | LCS + DP | 두 파일 줄 수 M, N에 대해 시간·공간 O(MN) |

- V는 커밋 수, E는 부모 연결 수다. 정렬의 N은 원소 수다. 문자열 비교 비용 등은 별도로 고려해야 한다.
- `deque`: double-ended queue, 양쪽 끝에서 넣고 꺼낼 수 있는 큐.
- DAG: Directed Acyclic Graph, 방향성 비순환 그래프. 부모 관계에 순환이 없어야 부모 우선 로그를 만들 수 있다.
- LCS: Longest Common Subsequence, 최장 공통 부분 수열.
- DP: Dynamic Programming, 동적 계획법. 작은 문제의 계산 결과를 표에 저장해 재사용한다.
- SHA-1: Secure Hash Algorithm 1. 여기서는 내용·시각·난수로 커밋 식별자 후보를 만드는 데 쓴다. 암호화나 비밀키 생성 용도가 아니다.

<br><br>

## 🟢 7. 테스트 실행

앱에서 `EXIT`로 나온 뒤, 프로젝트 최상위 폴더의 터미널에서 실행한다.

```bash
# 전체 테스트 파일을 찾아 실행한다.
uv run --locked python -m unittest discover -s tests -p 'test_*.py'
# 그래프 관련 테스트 모듈만 자세한 결과와 함께 실행한다.
uv run --locked python -m unittest tests.test_graph -v
```

| 명령·옵션 | 의미 |
| --- | --- |
| `unittest` | unit test, Python 표준 단위 테스트 도구 |
| `discover` | 테스트 자동 검색 |
| `-s tests` | start directory, 검색 시작 폴더 지정 |
| `-p 'test_*.py'` | pattern, 테스트 파일 이름 규칙. 따옴표는 셸이 먼저 확장하지 않게 함 |
| `tests.test_graph` | `tests/test_graph.py` 모듈 지정 |
| `-v` | verbose, 테스트 이름과 결과를 자세히 출력 |

성공하면 마지막에 `Ran ... tests`와 `OK`가 나온다. 테스트 개수는 파일이 추가되면 달라질 수 있다.

| 테스트 | 확인 대상 |
| --- | --- |
| `test_cli.py` | 입력 해석, 명령 실행, 브랜치 목록 |
| `test_services.py`, `test_repositories.py` | 서비스 흐름과 상태 보관 |
| `test_graph.py` | 부모 우선 정렬, 경로, 조상, 순환 검사 |
| `test_index.py`, `test_sort.py` | 검색과 정렬 |
| `test_models.py`, `test_validators.py` | 커밋 모델과 입력 유효성 |
| `test_refactoring.py`, `test_regressions.py` | 기능 연결과 이전 오류의 재발 방지 |

<br><br>

## 🟢 8. 자주 만나는 문제

| 증상 | 확인할 것 |
| --- | --- |
| `command not found: uv` | uv 설치 후 터미널을 새로 열고 설치 안내의 PATH 설정 확인. PATH는 실행 파일 검색 경로 |
| `No module named git-app` | 프로젝트 최상위 폴더인지 확인. 폴더명은 `git_app`이 아니라 `git-app` |
| 잠금 파일 변경이 필요하다는 오류 | `pyproject.toml`과 `uv.lock`이 같은 프로젝트 버전인지 확인. 원인 확인 없이 잠금 파일을 삭제하지 않음 |
| Python 다운로드 실패 | 인터넷 연결과 접근 제한 확인. 이미 설치한 Python도 3.10 이상이어야 함 |
| 초기화가 필요하다는 안내 | 앱 안에서 `INIT "이름"`부터 실행 |
| `Unknown commit` | 현재 실행에서 나온 실제 해시인지 확인. 이전 실행의 번호는 사용할 수 없음 |
| `No path` | 서로 분리된 기록이거나 `--directed` 방향으로 도달할 수 없는 경우 |
| 검색 결과가 없음 | 전체 단어 일치, 여러 단어의 AND 조건, 작성자 전체 이름 확인 |
| `Invalid args` | 따옴표, 허용 옵션, 인자 개수 확인. `HELP`로 문법 조회 |
| 재시작 후 기록이 없음 | 정상 동작. 메모리 저장 방식이며 파일 저장 기능은 없음 |

<br><br>

## 🟢 9. Docker로 실행하기 — 선택 사항

로컬 실습을 마친 뒤 진행한다. Docker가 설치되어 있고 실행 중이어야 한다. 먼저 직접 이미지를 받아 컨테이너를 실행하고, 그다음 제공된 Dockerfile·Compose를 사용한다. 컨테이너에는 Python이 있으므로 uv 없이 실행한다.

### 🟡 9-1. 이미지 다운로드와 직접 실행

프로젝트 최상위 폴더에서 실행한다. 소스 폴더만 읽기 전용으로 연결한다.

```bash
# Python 3.11 실행 환경 이미지를 받는다.
docker pull python:3.11-slim
# 소스 폴더만 연결한 임시 컨테이너에서 앱을 실행한다.
docker run --rm -it --mount "type=bind,source=$(pwd)/git-app,target=/app/git-app,readonly" -w /app -e PYTHONDONTWRITEBYTECODE=1 python:3.11-slim python -m git-app
```

| 부분 | 의미 |
| --- | --- |
| `docker pull` | 컨테이너를 만들 원본 이미지 다운로드 |
| `docker run` | 이미지에서 컨테이너를 만들어 실행 |
| `--rm` | 종료한 컨테이너 자동 제거. 호스트 소스나 이미지를 지우는 옵션은 아님 |
| `-i`, `-t` | interactive, tty(teletypewriter): 입력 유지와 대화형 터미널 할당 |
| `--mount` | 호스트 소스 폴더를 컨테이너에 연결 |
| `type=bind` | 기존 호스트 경로를 연결하는 방식 |
| `source`, `target`, `readonly` | 호스트 경로, 컨테이너 경로, 읽기 전용 |
| `$(pwd)` | print working directory, 현재 폴더 경로를 명령 안에 넣음 |
| `-w /app` | workdir, 컨테이너의 작업 폴더 |
| `-e` | environment, 컨테이너 환경변수 설정 |
| `PYTHONDONTWRITEBYTECODE=1` | 읽기 전용 소스에 바이트코드 캐시 파일을 쓰지 않음 |
| `python:3.11-slim` | Python 3.11 기반의 경량 이미지 |

이 방식은 `git-app`만 연결하므로 호스트의 다른 파일은 컨테이너 안에서 바로 보이지 않는다.

### 🟡 9-2. Dockerfile과 Compose 사용

```bash
# 현재 폴더의 Dockerfile로 앱 이미지를 만든다.
docker build -t mini-git .
# 만든 이미지로 대화형 앱을 실행한다.
docker run --rm -it mini-git
```

여기서 `build`는 이미지 만들기, `-t`는 tag(이미지 이름표), `.`은 현재 폴더를 빌드 입력으로 지정한다. `docker run`의 `-t`는 터미널 옵션이므로 같은 글자라도 명령에 따라 뜻이 다르다.

Compose를 사용하면 위 두 명령 대신 다음 명령으로 실행할 수 있다.

```bash
# compose.yaml의 mini-git 서비스 이미지를 빌드한 뒤 일회성으로 실행한다.
docker compose run --build --rm mini-git
```

`compose`는 설정 파일로 컨테이너 실행을 관리하는 도구다. `run`은 서비스의 일회성 실행, `--build`는 실행 전 이미지 빌드, `--rm`은 종료한 컨테이너 제거다. Dockerfile은 앱 소스와 테스트만 복사한다. 컨테이너를 사용해도 커밋 기록이 영구 저장되지는 않는다.

<br><br>

## 🟢 10. 사용 범위와 보안

- 실제 Git 저장소를 초기화하거나 파일을 커밋하는 프로그램이 아니다. `.git`의 실제 이력을 수정하지 않는다.
- 앱 상태는 메모리에만 유지한다. 중요한 실제 작업 이력을 보관하는 용도로 사용하지 않는다.
- 해시 후보는 저장소와 세션 발급 이력을 검사한다. 32번 연속 충돌하면 카운터 후보로 전환한다. 영구적·분산 환경의 유일성을 보장하는 설계는 아니다.
- `DIFF`는 알려진 환경 파일·개인 키 이름과 심볼릭 링크의 실제 대상 이름을 검사한다. 임의 이름의 파일에 들어 있는 비밀값까지 탐지하지는 못한다. 민감한 파일을 입력하지 않는다.
- `DIFF`의 동적 계획법은 큰 파일에서 시간과 메모리를 많이 쓸 수 있으므로 작은 텍스트 파일부터 비교한다.
- 환경 파일, 인증 키, 개인 경로, 비공개 문서는 저장소나 실행 출력에 공유하지 않는다.
