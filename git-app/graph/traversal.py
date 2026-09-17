from graph.paths import bfs_shortest_path, get_ancestors, path_step_key  # 경로·조상 알고리즘을 불러옴.
from graph.topological import topological_sort, topological_sort_with_priority  # 부모 우선 정렬을 불러옴.


# 기존 서비스와 테스트가 쓰는 호출 이름을 유지하는 작은 연결 창구임.
class GraphTraversal:
    topological_sort = staticmethod(topological_sort)  # 기본 LOG를 부모 우선 정렬에 연결함.
    topological_sort_with_priority = staticmethod(topological_sort_with_priority)  # 작성자 우선 연습을 연결함.
    bfs_shortest_path = staticmethod(bfs_shortest_path)  # PATH를 경로 탐색에 연결함.
    get_ancestors = staticmethod(get_ancestors)  # ANCESTORS를 부모 탐색에 연결함.
    _path_step_key = staticmethod(path_step_key)  # 이전 비교 기준 함수의 호출 이름도 유지함.
