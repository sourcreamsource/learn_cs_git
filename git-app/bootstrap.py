# 설명: 
# 1. 필요한 모듈이나 클래스를 불러옵니다.
# 2. 앱이 필요로 하는 객체(서비스, 저장소 등)를 하나씩 만듭니다.
# 3. 필요한 객체는 서로 의존하는 경우가 많으므로, 의존하는 객체를 먼저 만들고 연결합니다.
# 4. 모든 부품이 연결된 최종 앱 객체를 반환합니다.

# 🔥 CLI 커맨드 디스패처 클래스를 불러옴
from cli.commands import CommandDispatcher  # 명령을 담당자에게 전달하는 창구임.

# 🔥 하이브리드 CLI REPL 엔진 클래스를 불러옴
from cli.hybrid_cli import HybridCLI  # 사용자 입력을 반복해서 받는 화면임.

# 역색인 클래스를 불러옴
from index.inverted_index import InvertedIndex  # 단어·작성자 검색용 보관함임.

# 브랜치 저장소 클래스를 불러옴
from repositories.branch_repository import BranchRepository  # 브랜치·HEAD·사용자를 보관함.

# 커밋 저장소 클래스를 불러옴
from repositories.commit_repository import CommitRepository  # 해시별 커밋을 보관함.

# 보너스 기능 서비스 클래스를 불러옴
from services.bonus_service import BonusService  # 선택 과제의 작업을 담당함.

# Git 핵심 서비스 클래스를 불러옴
from services.git_service import GitService  # 저장소 변경을 담당함.

# 그래프 탐색 서비스 클래스를 불러옴
from services.graph_service import GraphService  # 부모 관계에 따른 조회를 담당함.

# 검색 및 정렬 서비스 클래스를 불러옴
from services.search_service import SearchService  # 검색과 기준별 정렬을 담당함.

# 해시 생성기 클래스를 불러옴
from utils.hash_generator import HashGenerator  # 이 앱 세션에서 쓸 번호 발급기임.


# 앱 부품은 여기서 한 번 만들고 필요한 서비스에 같은 객체를 전달함.
def create_app() -> HybridCLI:
    """공유 저장소와 서비스를 연결하고 실행 가능한 입력 화면을 반환한다.

    커밋·브랜치·색인·해시 생성기를 한 번씩 만들어
    필요한 서비스에 같은 객체를 전달한다. 일반 커밋과 병합도
    동일한 기록과 해시 발급 이력을 사용한다.
    반환된 HybridCLI의 실행은 호출자가 맡는다.
    """
    commits = CommitRepository()  # 모든 서비스가 공유할 커밋 보관함임.
    
    branches = BranchRepository()  # 모든 서비스가 공유할 브랜치 상태임.
    index = InvertedIndex()  # 커밋과 병합이 함께 갱신할 색인임.
    hasher = HashGenerator()  # 일반 커밋과 병합이 발급 이력을 공유함.
    git = GitService(commits, branches, index, hasher)  # 저장소 변경 서비스에 공유 부품을 연결함.
    graph = GraphService(commits, branches)  # 조회 서비스도 같은 기록을 보게 함.
    search = SearchService(commits, index)  # 검색 서비스에 기록과 색인을 연결함.
    bonus = BonusService(commits, branches, index, hasher)  # 병합도 같은 저장소와 번호 발급기를 사용함.
    dispatcher = CommandDispatcher(git, graph, search, bonus)  # 명령 연결표를 구성함.
    return HybridCLI(dispatcher)  # 부품 연결이 끝난 입력 화면을 반환함.
