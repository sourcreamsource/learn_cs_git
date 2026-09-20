from cli.interactive import InteractiveHandler  # 조회 인자가 없으면 사용자에게 질문함.
from cli.presenter import show_ancestors, show_log, show_path, show_search_results  # 조회 결과 형식을 재사용함.

from services.graph_service import GraphService  # 로그·경로·조상 탐색을 요청할 서비스임.

from services.search_service import SearchService  # 검색·기준별 정렬을 요청할 서비스임.


# LOG·PATH·ANCESTORS·SEARCH처럼 기록을 조회하는 명령을 담당함.
class HistoryCommands:
    
    def __init__(self, graph_service: GraphService, search_service: SearchService) -> None:  # 조회 서비스만 받음.
        self._graph = graph_service  # 부모 관계를 이용하는 조회를 맡김.
        self._search = search_service  # 색인과 정렬을 이용하는 조회를 맡김.



    # ✅ 
    # 기본 또는 기준별 로그를 선택함.
    def handle_log(self, args: list[str], options: dict[str, str]) -> None:  

        # 1. 정렬 옵션이 없는 경우
        if "sort-by" not in options:                        # 정렬 옵션이 없으면 부모 우선 로그임.    
            show_log(self._graph.get_topological_log())     # 🔥🔥🔥🔥🔥 위상정렬된 log를 브랜치 이름표와 함께 출력함.
            return                                          # 기본 로그 출력을 마침.
        
        
        # 2. 옵션이 있다면!
        success, commits, message = self._search.get_sorted_log(options["sort-by"])  # 날짜·작성자 정렬을 요청함.
        
        if not success or commits is None:                  # 잘못된 정렬 기준을 처리함.
            print(message)                                  # 서비스의 검증 오류를 보여 줌.
            return                                          # 잘못된 기준으로 출력하지 않음.
        
        entries = []                                        # 공통 로그 출력기에 넘길 목록임.
        
        for commit in commits:                              # 정렬된 순서를 그대로 사용함.
            entries.append((commit, []))                    # 기존 정렬 LOG처럼 브랜치 이름표를 생략함.
        
        show_log(entries)                                   # 기본 LOG와 같은 커밋 표시 형식을 사용함.



    # ✅ 
    # 두 커밋 사이의 경로를 찾음.
    def handle_path(self, args: list[str], options: dict[str, str]) -> None:  
        
        start, end = InteractiveHandler.ask_path(args)  # 빠진 번호만 질문함.
        
        if not start or not end:  # 두 번호 중 하나가 빠졌는지 확인함.
            print("Invalid args: two commit hashes required (PATH <commit1> <commit2>)")  # 필요한 인자를 알려 줌.
            return  # 탐색하지 않음.
        
        direction = options.get("directed", "false").lower()  # 기본은 양방향 탐색임.
        
        if direction not in ("true", "false"):  # 확장 옵션의 값을 확인함.
            print("Invalid args: --directed must be true or false")  # 잘못된 방향 값을 알려 줌.
            return  # 잘못된 조건으로 탐색하지 않음.
        
        success, path, message = self._graph.get_shortest_path(start, end, directed=direction == "true")  # 경로를 요청함.
        
        if not success:  # 존재하지 않는 번호 등의 오류인지 확인함.
            print(message)  # No path와 구분되는 오류를 출력함.
            return  # 경로 출력은 하지 않음.
        
        show_path(path)  # 연결 없음 또는 실제 경로를 출력함.



    # ✅
    def handle_ancestors(self, args: list[str], options: dict[str, str]) -> None:  # 모든 조상을 조회함.
        commit_hash = InteractiveHandler.ask_ancestors(args)  # 대상 번호를 받음.

        if not commit_hash:  # 번호 입력이 취소되었는지 확인함.
            print("Invalid args: commit hash is required")  # 번호가 필요함을 알림.
            return  # 조회하지 않음.
        
        success, ancestors, message = self._graph.get_ancestors(commit_hash)  # 부모 방향 탐색을 요청함.
        
        if not success or ancestors is None:  # 알 수 없는 번호인지 확인함.
            print(message)  # 서비스의 오류를 알려 줌.
            return  # 잘못된 결과를 출력하지 않음.
        
        show_ancestors(commit_hash, ancestors)  # 조상 목록 또는 뿌리 안내를 출력함.



    # ✅
    def handle_search(self, args: list[str], options: dict[str, str]) -> None:  # 작성자 또는 단어 색인을 선택함.
        
        # 1. author 옵션일 경우,
        if "author" in options:  # 작성자 검색 옵션이 있는 경우임.
            if args:  # 작성자와 단어를 동시에 지정하면 뜻이 모호함.
                print("Invalid args: use a keyword or --author, not both")  # 검색 방식 하나만 선택하게 함.
                return  # 모호한 검색을 실행하지 않음.
            
            author = options["author"]  # 작성자 이름을 가져옴.
            
            if not author.strip():  # 공백뿐인 이름은 거부함.
                print("Invalid args: author name is required")  # 올바른 작성자 이름이 필요함을 알림.
                return  # 빈 이름으로 검색하지 않음.
            
            show_search_results(self._search.search_by_author(author))  # 작성자 색인의 결과를 출력함.
            
            return  # 작성자 검색을 마침.


        # 2. 일반
        keyword = InteractiveHandler.ask_search(args)  # 단어가 없으면 질문함.
        
        
        if not keyword or not keyword.strip():  # 빈 검색어인지 확인함.
            print("Invalid args: search keyword or --author=<name> is required")  # 필요한 검색값을 알려 줌.
            return  # 빈 검색어를 실행하지 않음.
        
        
        show_search_results(self._search.search_by_keyword(keyword))  # 단어 색인 결과를 출력함.

