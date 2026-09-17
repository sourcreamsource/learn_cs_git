from bootstrap import create_app  # 앱 조립은 bootstrap에 맡기고 기존 import 경로도 유지함.


# 프로그램을 조립한 뒤 사용자 입력 반복을 시작하는 단일 시작점임.
def main() -> None:
    app = create_app()  # 연결된 서비스와 CLI를 준비함.
    app.start_repl()  # Read-Eval-Print Loop, 입력·실행·출력·반복을 시작함.


if __name__ == "__main__":  # 모듈 또는 파일로 직접 실행했을 때만 시작함.
    main()  # Mini Git을 실행함.
