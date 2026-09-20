# 다른 파일에 쪼개져 있는 경로 탐색(BFS) 및 조상 찾기 알고리즘 함수들을 가져옴.
from graph.paths import bfs_shortest_path, get_ancestors, path_step_key  # 최단 경로 탐색(bfs), 조상 찾기(ancestors), 경로 정렬 기준 함수를 불러옴.

# 다른 파일에 쪼개져 있는 커밋 순서 정렬(위상 정렬) 알고리즘 함수들을 가져옴.
from graph.topological_sort import topological_sort, topological_sort_with_priority  # 기본 위상 정렬과 우선순위 정렬 함수를 불러옴.


# 여기저기 흩어진 그래프 탐색 기능들을 한곳에서 편하게 꺼내 쓰도록 모아둔 안내 데스크(허브) 클래스임.
class GraphTraversal:
    """분리된 그래프 함수를 정적 메서드로 제공하는 공통 호출 창구다.

    LOG는 topological_sort, PATH는 bfs_shortest_path,
    ANCESTORS는 get_ancestors로 연결한다. 여기서 알고리즘을 복제하지 않는다.
    객체를 만들지 않고 GraphTraversal.함수명으로 호출할 수 있다.
    """
    topological_sort = staticmethod(topological_sort)  # 커밋들을 부모-자식 순서대로 바르게 줄 세우는 정렬 함수를 연결함.
    topological_sort_with_priority = staticmethod(topological_sort_with_priority)  # 작성자 이름 등의 우선순위를 따져서 줄 세우는 정렬 함수를 연결함.
    bfs_shortest_path = staticmethod(bfs_shortest_path)  # 두 커밋 사이의 가장 가까운 지름길(최단 경로)을 찾는 함수를 연결함.
    get_ancestors = staticmethod(get_ancestors)  # 특정 커밋의 조상(부모, 할아버지 등) 커밋들을 족보처럼 거슬러 올라가 찾는 함수를 연결함.
    _path_step_key = staticmethod(path_step_key)  # 경로를 탐색할 때 어느 쪽 길을 먼저 갈지 결정하는 기준 함수를 연결함.


    # [ staticmethod(함수)가 여기에 쓰인 이유와 역할 ]
    # 1. 왜 @staticmethod 대신 staticmethod(...) 함수 형태로 썼는가?
    #    - 보통은 'def 함수' 위에 '@staticmethod'를 붙이지만, 여기에 있는 함수들은 다른 파일에서 이미 만들어져서 import로 가져온 함수임.
    #    - 이렇게 이미 만들어진 외부 함수를 클래스에 정적 메서드로 붙일 때는 staticmethod(외부함수) 형태로 감싸서 등록함.
    # 2. 정확히 어떤 역할을 하는가?
    #    - GraphTraversal 객체(인스턴스)를 따로 만들지 않고도 GraphTraversal.topological_sort(...) 처럼
    #      클래스 이름으로 외부 함수를 곧바로 호출할 수 있게 해 주는 '안내 데스크(연결 창구)' 역할을 함.
    #    - 즉, @staticmethod와 100% 똑같은 기능을 하지만, 외부 함수를 클래스에 연결하기 위해 이 문법을 사용한 것임.
