# 데이터 클래스를 정의하기 위해 dataclass와 field를 불러옴
from dataclasses import dataclass, field
# 현재 날짜와 시간을 포맷팅하기 위해 datetime 모듈을 불러옴
from datetime import datetime
# 리스트와 딕셔너리 등 타입 힌트를 위해 typing 모듈을 불러옴
from typing import Any, Dict, List


# 커밋을 만들 때 사용할 현재 시각 문자열을 만드는 쉬운 이름의 함수임
def create_current_timestamp() -> str:
    # 현재 시각을 요구사항의 읽기 쉬운 문자열 형식으로 바꾸어 반환함
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Git의 기본 저장 단위인 커밋 노드를 나타내는 데이터 클래스임
@dataclass
# 준비한 값으로 이 단계의 작업을 실행함.
class Commit:
    # 커밋의 고유한 식별자 해시 문자열임 (예: a1b2c3)
    hash: str
    # 커밋에 대한 설명 메시지 문자열임 (예: Initial commit)
    message: str
    # 커밋을 작성한 사람의 이름임 (예: Alice)
    author: str
    # 커밋이 생성된 날짜와 시간 문자열임 (기본값은 현재 시간 문자열로 자동 설정)
    timestamp: str = field(default_factory=create_current_timestamp)
    # 직전 부모 커밋들의 해시 문자열 목록임 (최초 커밋은 0개, 일반 커밋은 1개, 병합 커밋은 2개)
    parents: List[str] = field(default_factory=list)

    # 커밋 객체를 화면에 보기 좋은 문자열 형태로 변환하는 함수임
    def __str__(self) -> str:
        # 부모 정보 문자열을 만듦
        parents_str = "root"
        # 부모가 하나 이상이면 부모 해시들을 쉼표로 이어 붙임
        if self.parents:
            # 다음 단계에서 쓸 값을 계산하거나 꺼내 변수에 보관함.
            parents_str = ", ".join(self.parents)
        # 식별 가능한 형식으로 포맷팅하여 반환함
        return f"commit {self.hash} ({self.author}, {self.timestamp}) [parents: {parents_str}]\n{self.message}"

    # 커밋 객체를 딕셔너리 형태로 변환하는 편의 함수임
    def to_dict(self) -> Dict[str, Any]:
        # 내부 필드들을 딕셔너리로 묶어서 반환함
        return {
            # 해시 필드
            "hash": self.hash,
            # 메시지 필드
            "message": self.message,
            # 작성자 필드
            "author": self.author,
            # 타임스탬프 필드
            "timestamp": self.timestamp,
            # 부모 목록 필드
            "parents": list(self.parents),
        # 앞에서 여러 줄로 적은 값이나 설정의 묶음을 마무리함.
        }
