# 따옴표로 묶인 공백 포함 문자열을 안전하게 파싱하기 위해 shlex 모듈을 불러옴
import shlex
# 타입 힌트를 위해 Dict, List, Optional, Tuple을 불러옴
from typing import Dict, List, Optional, Tuple


# 사용자가 터미널에 입력한 한 줄 문자열을 파싱하는 클래스임 (대소문자 무시, 따옴표 지원, 옵션 분리)
class CommandParser:
    # 한 줄의 명령 문자열을 (명령어, 위치인자리스트, 옵션딕셔너리) 튜플로 파싱하는 함수임
    
    # [ @staticmethod 정적 메서드 데코레이터 설명 ]
    # 1. 역할: 객체(인스턴스)를 따로 만들지 않고도, 클래스 이름에서 바로 함수를 호출할 수 있게 해 줌.
    #    - 일반 메서드: parser = CommandParser() 로 객체를 만든 뒤 parser.parse_line(line) 호출
    #    - 정적 메서드: CommandParser.parse_line(line) 처럼 객체 생성 없이 클래스 이름으로 바로 호출 가능
    # 2. self가 필요 없는 이유:
    #    - 일반 메서드는 클래스 내부의 저장된 데이터(변수)를 다루기 위해 첫 번째 인자로 'self'를 받음.
    #    - 하지만 parse_line은 내부 데이터를 전혀 만지지 않고, 오직 전달받은 'line' 문자열만 분석하는 독립적인 도구(유틸리티) 함수이므로 self가 필요 없음.
    @staticmethod
    # 아래 작업을 이름으로 다시 호출할 수 있게 함수로 정의함.
    def parse_line(
        # 이 항목의 이름과 사용할 값 또는 자료형을 지정함.
        line: str,
    # 앞에서 여러 줄로 적은 값이나 설정의 묶음을 마무리함.
    ) -> Tuple[Optional[str], List[str], Dict[str, str]]:


        # 문자열 앞뒤 공백을 제거함
        cleaned = line.strip()
        # 입력이 비어있는 경우 모두 빈 값으로 반환함
        
        if not cleaned:
            # 처리 결과를 호출한 곳에 돌려주고 이 함수의 실행을 끝냄.
            return None, [], {}

        # 중단 신호나 오류가 날 수 있는 작업을 시도함.
        try:
            # shlex를 사용하여 공백 기준 분리하되 따옴표 내부 공백은 유지함 (POSIX 표준 준수)
            tokens = shlex.split(cleaned)
        # 지정한 오류나 중단 신호가 발생했을 때 아래에서 처리함.
        except ValueError:
            # 닫히지 않은 따옴표는 뜻이 달라질 수 있으므로 억지로 실행하지 않고 파싱 오류를 반환함
            return None, [], {"parse-error": "unmatched quote"}

        # 토큰이 없으면 빈 값 반환
        if not tokens:
            # 처리 결과를 호출한 곳에 돌려주고 이 함수의 실행을 끝냄.
            return None, [], {}

        # 첫 번째 토큰은 명령어 이름이며, 대소문자 구분을 하지 않도록 대문자로 정규화함 (예: init -> INIT)
        action = tokens[0].upper()

        # 위치 인자들을 담을 리스트임
        args: List[str] = []
        
        # --key=value 형태의 옵션들을 담을 딕셔너리임
        options: Dict[str, str] = {}
        
        # -- 뒤의 글자는 옵션처럼 보여도 일반 인자로 읽음.
        options_finished = False

        
        
        # 두 번째 토큰부터 순회하며 옵션과 인자를 분류함
        for token in tokens[1:]:

            # '--'로 시작하는 옵션 플래그인 경우
            if token == "--" and not options_finished:
                # 옵션 해석을 여기서 끝냄.
                options_finished = True
                # 구분자 자체는 인자로 넣지 않음.
                continue
            
            # 구분자 앞의 --이름만 옵션으로 읽음.
            if token.startswith("--") and not options_finished:
                # '--' 접두사를 제거함
                opt_str = token[2:]
                # '=' 기호가 포함되어 키와 값이 나뉘는 경우
                if "=" in opt_str:
                    # 다음 단계에서 쓸 값을 계산하거나 꺼내 변수에 보관함.
                    key, val = opt_str.split("=", 1)
                # 앞의 조건에 해당하지 않는 나머지 경우를 처리함.
                else:
                    # directed만 값을 생략할 수 있는 켜기 옵션임.
                    if opt_str.lower() != "directed":
                        # author와 sort-by에는 등호와 값이 필요함.
                        return None, [], {"parse-error": "use --name=value"}
                    # 단독 --directed는 참이라는 뜻임.
                    key, val = opt_str, "true"
                # 옵션 이름의 대소문자 차이를 없앰.
                key = key.lower()
                # 빈 값이나 중복 옵션은 실행하지 않음.
                if not key or not val.strip() or key in options:
                    # 마지막 값으로 조용히 덮어쓰지 않고 오류를 알림.
                    return None, [], {"parse-error": "empty or duplicate option"}
                # shlex가 문법용 따옴표를 처리했으므로 내용은 그대로 보관함.
                options[key] = val
            
            # 앞의 조건에 해당하지 않는 나머지 경우를 처리함.
            else:
                # 메시지 내용에 포함된 따옴표도 그대로 보관함.
                args.append(token)

        # 최종 파싱 결과 (명령어, 위치 인자 목록, 옵션 딕셔너리)를 반환함
        return action, args, options
