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
    """커밋 식별자 후보를 만드는 방식의 공통 규약이다.

    generate를 구현한 전략으로 카운터와 난수 방식을 교체한다.
    후보 생성과 중복 검사는 다른 책임이며 전략만으로 유일성을 보장하지 않는다.
    """
    # 새로운 해시 문자열을 생성하는 추상 메서드임
    @abstractmethod
    # 자식 클래스에서 반드시 구현해야 하는 해시 생성 함수임
    def generate(self, content: str = "") -> str:
        # 추상 메서드이므로 pass로 비워둠
        pass


# 1부터 숫자가 1씩 증가하는 카운터 기반 해시 생성기 클래스임 (테스트 및 재현성 우수)
class CounterHashStrategy(HashStrategy):
    """증가하는 정수를 16진수 식별자로 만드는 재현 가능한 전략이다.

    새 객체에서 같은 순서로 호출하면 같은 번호가 나온다.
    content는 번호 생성에 사용하지 않고 prefix는 번호 앞에 붙인다.
    서로 다른 객체나 실행 사이의 중복까지 막지는 않는다.
    """
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
    """내용·시각·난수로 SHA-1(Secure Hash Algorithm 1) 후보를 만든다.

    같은 내용이어도 실행 시점과 난수에 따라 달라질 수 있다.
    기본 6자리로 잘라 쓰므로 충돌할 수 있고 중복 검사가 따로 필요하다.
    암호화, 비밀번호 보호, 비밀키 생성 용도로 사용하는 클래스가 아니다.
    """
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
    """식별자 생성 전략과 같은 객체의 발급 이력을 관리한다.

    기본은 난수 전략이고 테스트에서는 카운터로 교체할 수 있다.
    이름에 Generator가 있어도 yield로 값을 내보내는 파이썬 제너레이터는 아니다.
    유일성 검사가 필요할 때는 next_hash가 아닌 next_unique_hash를 쓴다.
    """
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
        """후보 생성 방식만 바꾸고 기존 발급 이력과 대체 카운터는 유지한다.

        입력은 HashStrategy 구현 객체이고 반환값은 None이다.
        전략 교체가 저장된 커밋 해시나 발급 이력을 초기화하지는 않는다.
        """
        self._strategy = strategy

    # 설정된 전략을 사용해 새 해시를 생성하고 반환하는 함수임
    def next_hash(self, content: str = "") -> str:
        # 전략의 generate 함수를 호출하여 해시 결과를 얻고 반환함
        """현재 전략으로 후보 문자열 하나를 만든다.

        중복 검사나 발급 이력 등록은 하지 않는다.
        실제 저장에 필요한 유일성 검사는 next_unique_hash가 담당한다.
        """
        return self._strategy.generate(content)

    # 저장소의 존재 검사 함수를 받아 아직 없는 번호만 발급함.
    def next_unique_hash(self, content: str, exists: Callable[[str], bool]) -> str:
        # 난수 전략이 계속 충돌하더라도 무한히 기다리지 않음.
        """세션 발급 이력과 저장소 양쪽에 없는 식별자를 찾아 반환한다.

        content는 후보 재료, exists는 저장소에 번호가 있는지 검사하는 함수다.
        후보를 최대 32번 검사하고 계속 충돌하면
        c 접두사가 붙은 증가 카운터로 전환해 빈 번호를 찾는다.
        발급 이력은 이 객체가 살아 있는 동안 유지되며 앱 재시작까지
        영구 보존되거나 동시 실행 간 원자적으로 보호되는 것은 아니다.
        """
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
