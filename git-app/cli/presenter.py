from models.commit import Commit  # 출력할 커밋의 자료형을 불러옴.
from constants.messages import MSG_NO_COMMITS_FOUND, MSG_NO_COMMITS_YET, MSG_NO_PATH  # 빈 결과 안내를 재사용함.


# 일반 커밋과 병합 커밋의 생성 결과를 같은 모양으로 출력함.
def show_created_commit(branch: str, commit: Commit) -> None:
    print(f"[{branch} {commit.hash}] {commit.message}")  # 브랜치·새 번호·메시지를 보여 줌.


# LOG 한 항목의 표시 형식을 한곳에서 관리함.
def show_commit(commit: Commit, branches: tuple[str, ...] | list[str] = ()) -> None:
    branch_info = ""  # 가리키는 브랜치가 없으면 추가 표시가 없음.
    if branches:  # 이 커밋을 가리키는 브랜치가 있을 때만 이름표를 붙임.
        branch_info = f" [{', '.join(branches)}]"  # 여러 브랜치를 쉼표로 연결함.
    print(f"commit {commit.hash} ({commit.author}, {commit.timestamp}){branch_info}")  # 식별 정보를 출력함.
    print(commit.message)  # 커밋 메시지는 다음 줄에 출력함.


# 기본 LOG와 정렬 LOG가 같은 출력 함수를 사용하도록 함.
def show_log(entries: list[tuple[Commit, list[str]]]) -> None:
    if not entries:  # 출력할 커밋이 없는지 확인함.
        print(MSG_NO_COMMITS_YET)  # 아직 기록이 없다고 알려 줌.
        return  # 빈 결과 처리를 마침.
    for commit, branches in entries:  # 서비스가 정한 순서를 그대로 유지함.
        show_commit(commit, branches)  # 커밋 하나를 공통 형식으로 출력함.


# 키워드 검색과 작성자 검색의 출력 형식을 공유함.
def show_search_results(commits: list[Commit]) -> None:
    if not commits:  # 검색 결과가 없는지 확인함.
        print(MSG_NO_COMMITS_FOUND)  # 검색 결과 없음 문구를 출력함.
        return  # 빈 결과 처리를 마침.
    noun = "commit"  # 결과가 하나일 때 쓰는 단어임.
    if len(commits) > 1:  # 두 개 이상이면 복수 표현을 씀.
        noun = "commits"  # 복수 단어로 바꿈.
    print(f"Found {len(commits)} {noun}:\n")  # 결과 개수와 빈 줄을 출력함.
    for commit in commits:  # 색인이 정한 결과 순서대로 보여 줌.
        print(f"- {commit.hash}: {commit.message}")  # 번호와 메시지를 출력함.


# 연결이 없는 경우와 실제 경로를 구분하여 출력함.
def show_path(path: list[str] | None) -> None:
    if path is None:  # 유효한 두 커밋 사이에 연결이 없는 경우임.
        print(MSG_NO_PATH)  # 경로가 없다고 알려 줌.
        return  # 경로를 연결하려고 시도하지 않음.
    print(f"Path: {' -> '.join(path)}")  # 출발점부터 목적지까지 화살표로 이어 보여 줌.


# 조상 결과를 발견 순서대로 출력함.
def show_ancestors(commit_hash: str, ancestors: list[str]) -> None:
    if not ancestors:  # 부모가 없는 뿌리 커밋인지 확인함.
        print(f"No ancestors found for commit {commit_hash} (root commit).")  # 조상이 없다고 알려 줌.
        return  # 뿌리 커밋의 결과 출력을 마침.
    print(f"Ancestors of {commit_hash} ({len(ancestors)} found):")  # 대상 커밋과 조상 수를 출력함.
    for ancestor in ancestors:  # 조상 번호를 순서대로 꺼냄.
        print(f"- {ancestor}")  # 한 줄에 조상 번호 하나를 출력함.
