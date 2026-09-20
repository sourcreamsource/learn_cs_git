# HELP 화면의 문구는 명령 실행 코드와 분리하여 여기서 수정함.
HELP_TEXT = """
================= 🟩 [Mini Git] 사용 가능한 명령어 목록 🟩 =================
  INIT <user_name>               : 저장소 초기화 (main 브랜치 및 작성자 설정)
  BRANCH <branch_name>           : 현재 커밋에서 새 브랜치 생성
  BRANCH LIST                    : 브랜치 목록 조회 (* = 현재 브랜치, LIST는 조회용 단어)
  SWITCH <branch_name>           : 지정한 브랜치로 HEAD 전환
  COMMIT <message>               : 현재 브랜치에 변경사항 커밋
  LOG                            : 부모가 먼저 출력되는 위상 정렬 커밋 이력 조회
  LOG --sort-by=date|author      : 날짜순 또는 작성자순으로 정렬된 커밋 이력 조회
  PATH <commit1> <commit2>       : 두 커밋 간의 무방향 BFS 최단 경로 탐색
  PATH <commit1> <commit2> --directed : 부모 방향으로만 탐색하는 경로 탐색
  ANCESTORS <commit_hash>        : 특정 커밋의 모든 조상 커밋 탐색
  SEARCH <keyword>               : 키워드로 커밋 메시지 역색인 검색
  SEARCH --author=<name>         : 작성자로 커밋 역색인 검색
  MERGE <branch_name>            : (보너스) 대상 브랜치를 현재 브랜치에 병합
  DIFF <file1> <file2>           : (보너스) 두 파일의 줄 단위 차이점 비교
  BENCH                          : (보너스) Merge Sort vs Quick Sort 속도 비교
  HELP                           : 도움말 보기
  QUIT / EXIT                    : Mini Git 종료

* 🔥 하이브리드 입력 방식: 인자 없이 명령어만 입력하면 친절한 대화형 프롬프트로 안내됩니다!

""".strip()  # 문구 앞뒤의 빈 줄을 제거해 기존 화면 출력을 유지함.
