from cli.commands import CommandDispatcher  # 명령을 담당자에게 전달하는 창구임.
from cli.hybrid_cli import HybridCLI  # 사용자 입력을 반복해서 받는 화면임.
from index.inverted_index import InvertedIndex  # 단어·작성자 검색용 보관함임.
from repositories.branch_repository import BranchRepository  # 브랜치·HEAD·사용자를 보관함.
from repositories.commit_repository import CommitRepository  # 해시별 커밋을 보관함.
from services.bonus_service import BonusService  # 선택 과제의 작업을 담당함.
from services.git_service import GitService  # 저장소 변경을 담당함.
from services.graph_service import GraphService  # 부모 관계에 따른 조회를 담당함.
from services.search_service import SearchService  # 검색과 기준별 정렬을 담당함.
from utils.hash_generator import HashGenerator  # 이 앱 세션에서 쓸 번호 발급기임.


# 앱 부품은 여기서 한 번 만들고 필요한 서비스에 같은 객체를 전달함.
def create_app() -> HybridCLI:
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
