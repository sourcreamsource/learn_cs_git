# hashlib 모듈을 불러와 SHA-1 해시 계산 기능을 사용함
import hashlib
# random 모듈을 불러와 무작위 난수 생성 기능을 사용함
import random
# 시간 정보를 가져오기 위해 time 모듈을 불러옴
import time
# 추상 클래스를 정의하기 위해 abc 모듈을 불러옴
from abc import ABC, abstractmethod
# 선택적으로 전달되는 해시 전략의 타입을 표시하기 위해 Optional을 불러옴
from typing import Callable, Optional


# 해시 생성기 인터페이스를 정의하는 추상 클래스임
class HashStrategy(ABC):
    # 새로운 해시 문자열을 생성하는 추상 메서드임
    @abstractmethod
    # 자식 클래스에서 반드시 구현해야 하는 해시 생성 함수임
    def generate(self, content: str = "") -> str:
        # 추상 메서드이므로 pass로 비워둠
        pass


# 1부터 숫자가 1씩 증가하는 카운터 기반 해시 생성기 클래스임 (테스트 및 재현성 우수)
class CounterHashStrategy(HashStrategy):
    # 생성자 함수로 카운터 시작 값을 0으로 초기화함
    def __init__(self, prefix: str = ""):
        # 카운터 숫자를 0으로 설정함
        self._count = 0
        # 해시 앞에 붙일 접두사를 저장함
        self._prefix = prefix

    # 카운터를 1 올리고 6자리 16진수 형태 문자열로 반환하는 함수임
    def generate(self, content: str = "") -> str:
        # 카운터 숫자를 1 증가시킴
        self._count += 1
        # 숫자를 6자리 16진수(예: 000001) 문자열로 포맷팅함
        hex_str = f"{self._count:06x}"
        # 접두사와 결합하여 반환함
        return f"{self._prefix}{hex_str}"


# SHA-1(Secure Hash Algorithm 1)과 시간·난수로 식별자를 만듦. 암호화나 비밀키 생성용이 아님.
class RandomShaHashStrategy(HashStrategy):
    # 해시 길이를 기본 6자리로 설정하는 생성자 함수임
    def __init__(self, length: int = 6):
        # SHA-1의 16진수 문자열 범위에서만 길이를 고르게 함.
        if not 1 <= length <= 40:
            # 빈 해시처럼 잘못된 결과를 만들 설정은 거부함.
            raise ValueError("Hash length must be between 1 and 40")
        # 자를 해시 길이를 저장함
        self._length = length

    # 입력 내용과 시간, 난수로 후보를 만듦. 유일성은 저장소 조회로 확인함.
    def generate(self, content: str = "") -> str:
        # 현재 시간을 초 단위 부동소수점 숫자로 가져옴
        now_time = str(time.time())
        # 0부터 999999 사이의 무작위 숫자를 뽑음
        rand_num = str(random.randint(0, 999999))
        # 내용과 시간과 난수를 합쳐서 원본 문자열을 만듦
        raw = f"{content}_{now_time}_{rand_num}"
        # SHA-1 알고리즘 객체를 생성함
        sha = hashlib.sha1()
        # 문자열을 바이트 형태로 인코딩하여 해시 객체에 전달함
        sha.update(raw.encode("utf-8"))
        # 16진수 문자열로 변환하고 지정한 길이(6자리)만큼 잘라서 반환함
        return sha.hexdigest()[: self._length]


# 전략 패턴을 적용하여 해시 생성 방식을 자유롭게 바꿀 수 있는 관리 클래스임
class HashGenerator:
    # 기본 해시 전략을 난수/SHA 전략으로 지정하는 생성자 함수임
    def __init__(self, strategy: Optional[HashStrategy] = None):
        # 기본 난수 SHA 해시 전략을 먼저 준비함
        self._strategy = RandomShaHashStrategy()
        # 전달된 전략이 있으면 기본 전략 대신 사용함
        if strategy is not None:
            # 다른 메서드에서도 사용할 수 있도록 객체 안에 보관함.
            self._strategy = strategy
        # 같은 후보가 계속 나오면 증가하는 번호로 탈출하기 위한 생성기임.
        self._fallback = CounterHashStrategy(prefix="c")
        # INIT을 다시 해도 같은 실행 세션에서 발급한 번호는 재사용하지 않음.
        self._issued = set()

    # 현재 사용 중인 해시 전략을 다른 전략으로 교체하는 함수임 (카운터 <-> 난수 전환 가능)
    def set_strategy(self, strategy: HashStrategy) -> None:
        # 내부 전략 객체를 새로운 전략으로 변경함
        self._strategy = strategy

    # 설정된 전략을 사용해 새 해시를 생성하고 반환하는 함수임
    def next_hash(self, content: str = "") -> str:
        # 전략의 generate 함수를 호출하여 해시 결과를 얻고 반환함
        return self._strategy.generate(content)

    # 저장소의 존재 검사 함수를 받아 아직 없는 번호만 발급함.
    def next_unique_hash(self, content: str, exists: Callable[[str], bool]) -> str:
        # 난수 전략이 계속 충돌하더라도 무한히 기다리지 않음.
        for attempt in range(32):
            # 설정된 전략에서 후보 번호를 받음.
            candidate = self.next_hash(content)
            # 빈 번호가 아니고 아직 저장되지 않은 번호여야 함.
            if candidate and candidate not in self._issued and not exists(candidate):
                # 저장소를 비운 뒤에도 중복을 막도록 발급 기록을 남김.
                self._issued.add(candidate)
                # 사용할 수 있는 번호를 반환함.
                return candidate
        # 반복 충돌 시 재현 가능한 카운터 번호로 전환함.
        candidate = self._fallback.generate()
        # 카운터 번호가 이미 쓰였으면 다음 번호를 확인함.
        while candidate in self._issued or exists(candidate):
            # 카운터는 계속 증가하므로 유한한 저장소에서 빈 번호를 찾음.
            candidate = self._fallback.generate()
        # 대체 번호도 같은 세션에서 재사용하지 않게 기억함.
        self._issued.add(candidate)
        # 빈 번호를 찾아 반환함.
        return candidate
