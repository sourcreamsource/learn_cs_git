from graph.topological import topological_sort  # 부모 우선 정렬을 그래프 검증에도 재사용함.
from models.commit import Commit  # 검사할 커밋 자료형임.


# DAG(Directed Acyclic Graph), 방향성 비순환 그래프의 조건을 검사함.
class DAGValidator:
    @staticmethod  # 순환 검사에 객체의 내부 상태가 필요하지 않음.
    def has_cycle(commits: dict[str, Commit]) -> bool:  # 그래프 내부의 순환 여부만 확인함.
        try:  # 정렬할 수 없는 순환을 찾아냄.
            topological_sort(commits, ignore_missing_parents=True)  # 외부 부모는 제외하고 내부 연결만 검사함.
        except ValueError:  # 모든 커밋을 부모 우선으로 처리할 수 없었음.
            return True  # 순환이 있다는 뜻임.
        return False  # 내부 연결에 순환이 없음.

    @staticmethod  # 전체 유효성도 객체 상태 없이 검사함.
    def validate(commits: dict[str, Commit]) -> bool:  # 부모 존재와 순환 없음을 함께 확인함.
        try:  # 기본 위상 정렬은 없는 부모도 오류로 처리함.
            topological_sort(commits)  # 커밋 객체를 복제하지 않고 연결을 검사함.
        except ValueError:  # 없는 부모 또는 순환을 발견한 경우임.
            return False  # 올바른 DAG가 아니라고 반환함.
        return True  # 부모가 모두 존재하고 순환도 없음.
