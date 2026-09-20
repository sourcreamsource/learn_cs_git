# 시스템 종료 및 입출력을 다루기 위해 sys 모듈을 불러옴
import sys

# 한 줄 명령 파서 클래스를 불러옴
from cli.parser import CommandParser

# CommandDispatcher 커맨드 핸들러 클래스를 불러옴
from cli.commands import CommandDispatcher





# Mini Git REPL(Read-Eval-Print Loop) 하이브리드 대화형 쉘 엔진 클래스임
class HybridCLI:
    # 커맨드 디스패처를 주입받아 초기화하는 생성자 함수임
    def __init__(self, dispatcher: CommandDispatcher) -> None:
        # 다른 메서드에서도 사용할 수 있도록 객체 안에 보관함.
        self._dispatcher = dispatcher

    # 사용자의 입력을 한 줄 받아 실행하는 함수임
    def execute_line(self, line: str) -> bool:

        # 🔥🔥🔥🔥🔥 한 줄 문자열을 명령어, 인자 리스트, 옵션 딕셔너리로 파싱함
        action, args, options = CommandParser.parse_line(line)

        # 따옴표 문법 오류가 있으면 원래 뜻을 추측하지 않고 표준 오류를 출력함
        if "parse-error" in options:
            # 사용자가 고칠 수 있는 일정한 오류 문구를 출력함
            print(f"Invalid args: {options['parse-error']}")
            # REPL은 계속 사용할 수 있도록 유지함
            return True

        # 빈 줄 입력이면 계속 진행함
        if not action:
            # 처리 결과를 호출한 곳에 돌려주고 이 함수의 실행을 끝냄.
            return True

        # 종료 명령어(QUIT, EXIT) 처리
        if action in ("QUIT", "EXIT"):
            # 종료 명령에는 인자나 옵션이 없어야 함.
            if args or options:
                # 잘못 입력한 종료 명령을 거부함.
                print("Invalid args: EXIT and QUIT take no arguments")
                # 정상 명령을 다시 입력할 수 있게 함.
                return True
            # 사용자가 확인할 결과나 안내를 화면에 출력함.
            print("Mini Git을 종료합니다. 안녕히 가세요!")
            # 처리 결과를 호출한 곳에 돌려주고 이 함수의 실행을 끝냄.
            return False

        # 🔥🔥🔥🔥🔥 공통 입력 검사를 거쳐 알맞은 명령 담당자에게 넘김.
        self._dispatcher.dispatch(action, args, options)

        # 종료 명령이 아니므로 다음 입력을 기다림.
        return True



    # ================================================================================
    # ✅ 시작점 - 프롬프트를 띄우고 무한 루프로 사용자 입력을 반복 처리하는 REPL 루프 실행 함수임
    def start_repl(self) -> None:
        # 사용자가 확인할 결과나 안내를 화면에 출력함.
        print("\n")
        print("⬛️" * 31)
        print("=" * 61)
        print("  🎊 Mini Git CLI에 오신 것을 환영합니다! 🎉")
        print("     옵션형 명령어 입력 및 대화형 입력을 모두 지원합니다.")
        print("     ('HELP' 입력 시 도움말)")
        print("=" * 61 + "\n")


        # =====================================================
        # 종료 신호가 올 때까지 반복 실행함
        while True:


            # 중단 신호나 오류가 날 수 있는 작업을 시도함.
            try:
                # 프롬프트를 출력하고 한 줄 입력을 받음
                user_input = input("mini-git> ")

                # 명령 실행 및 종료 여부 확인
                keep_running = self.execute_line(user_input)
                
                # 조건이 맞는 경우에만 아래 처리를 실행함.
                if not keep_running:
                    # 이 반복을 끝내고 반복문 다음으로 이동함.
                    break


            # 지정한 오류나 중단 신호가 발생했을 때 아래에서 처리함.
            except (KeyboardInterrupt, EOFError):
                # Ctrl+C 또는 Ctrl+D 인터럽트 발생 시 안전하게 종료함
                print("\nMini Git을 종료합니다.")
                # 이 반복을 끝내고 반복문 다음으로 이동함.
                break


            # 지정한 오류나 중단 신호가 발생했을 때 아래에서 처리함.
            except Exception:
                # 예기치 않은 오류 발생 시 프로그램이 튕기지 않도록 방어함
                # 내부 경로나 민감 정보를 드러내지 않는 일반 오류를 출력함
                print("Error occurred: unexpected error")
