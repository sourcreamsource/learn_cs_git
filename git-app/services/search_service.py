from index.inverted_index import InvertedIndex  # 단어·작성자로 후보 번호를 찾음.
from models.commit import Commit  # 검색 결과의 커밋 자료형임.
from repositories.commit_repository import CommitRepository  # 번호에 해당하는 실제 커밋을 가져옴.
from sort.merge_sort import merge_sort  # 정렬에는 직접 구현한 병합 정렬만 사용함.
from validators.input_validator import InputValidator  # 날짜·작성자 옵션을 검사함.


# 검색 후보를 실제 커밋으로 바꾸고, 로그의 정렬 기준을 선택함.
class SearchService:
    """색인으로 검색하고 날짜·작성자 기준 로그 정렬을 담당한다.

    색인은 후보 해시만 주고 저장소는 실제 Commit을 준다.
    부모 관계를 지키는 LOG는 GraphService의 별도 책임이다.
    """
    def __init__(self, commit_repo: CommitRepository, inverted_index: InvertedIndex) -> None:  # 필요한 두 보관함을 받음.
        self._commit_repo = commit_repo  # 커밋을 번호로 찾을 저장소임.
        self._index = inverted_index  # 검색 후보만 꺼낼 색인임.

    @staticmethod  # 날짜 비교는 객체의 다른 상태를 사용하지 않음.
    def _get_timestamp(commit: Commit) -> str:  # 날짜 정렬의 기준을 꺼냄.
        return commit.timestamp  # 고정된 연월일 형식이므로 문자열로 비교할 수 있음.

    @staticmethod  # 작성자 비교도 별도 상태가 필요하지 않음.
    def _get_normalized_author(commit: Commit) -> str:  # 작성자 정렬의 기준을 꺼냄.
        return commit.author.lower()  # 대소문자를 통일해 이름순으로 비교함.

    def _find_commits(self, hashes: list[str]) -> list[Commit]:  # 두 검색 방식의 결과 변환을 공유함.
        """색인에서 받은 해시만 조회하여 실제 커밋 목록으로 바꾼다.

        전체 저장소 순회 없이 후보 K개를 평균 O(K)에 조회한다.
        없는 해시는 건너뛰며 나머지는 전달된 해시 순서를 유지한다.
        """
        result = []  # 색인에서 찾은 커밋만 모을 바구니임.
        for commit_hash in hashes:  # 전체 저장소 대신 후보 번호만 읽음.
            commit = self._commit_repo.find_by_hash(commit_hash)  # 해시맵으로 커밋을 조회함.
            if commit is not None:  # 저장소에 있는 커밋만 반환함.
                result.append(commit)  # 색인의 등록 순서대로 결과에 넣음.
        return result  # 후보 K개를 조회한 결과를 반환함.




    # ------------------------------------------------------------------------------------------------
    # ✅
    def search_by_keyword(self, keyword: str) -> list[Commit]:  # 메시지의 단어 색인을 사용함.
        hashes = self._index.search_by_keyword(keyword)  # 여러 단어이면 공통 후보를 찾음.
        return self._find_commits(hashes)  # 찾은 번호들만 실제 커밋으로 바꿈.

    def search_by_author(self, author: str) -> list[Commit]:  # 작성자 전체 이름 색인을 사용함.
        hashes = self._index.search_by_author(author)  # 대소문자를 통일한 이름으로 번호를 찾음.
        return self._find_commits(hashes)  # 같은 결과 변환 절차를 사용함.




    # ------------------------------------------------------------------------------------------------
    # ✅
    def get_sorted_log(self, sort_by: str = "date") -> tuple[bool, list[Commit] | None, str]:  # 날짜·작성자순 로그를 반환함.
    
        # 1. 옵션 정제
        """전체 커밋을 date 또는 author 기준으로 안정 병합 정렬한다.

        반환값은 (성공 여부, 목록 또는 None, 안내 문구)다.
        잘못된 기준이면 실패하고 빈 저장소는 정상적인 빈 목록이다.
        날짜는 고정 형식 문자열, 작성자는 소문자 이름으로 비교한다.
        부모 선후관계까지 보장하는 함수가 아니다.
        부모 순서도 유지하려면 준비된 후보만 비교하는 우선순위 위상 정렬을 쓴다.
        """
        valid, option = InputValidator.validate_sort_option(sort_by)  # 자료를 꺼내기 전에 옵션을 검사함.
        
        # 2. 정제 실패 시 에러 처리
        if not valid:  # 지원하지 않는 정렬 기준을 거부함.
            return False, None, option  # 검증기가 만든 오류 문구를 반환함.
        
        # 3. 전체 커밋 가져오기
        commits = self._commit_repo.find_all()  # 로그에는 전체 커밋이 필요함.
        
        # 4. 전체 커밋이 없는 경우
        if not commits:  # 초기화 직후처럼 기록이 없는 경우임.
            return True, [], "Empty commits"  # 정상적인 빈 결과를 반환함.
        
        # 5. 날짜 정렬 기준 설정
        key_function = self._get_timestamp  # 기본은 날짜순임.
        
        # 6. 작성자 정렬을 요청한 경우
        if option == "author":  # 작성자 정렬을 요청한 경우임.
            key_function = self._get_normalized_author  # 비교값을 꺼내는 함수만 바꿈.
        
        # 7. 정렬 수행
        result = merge_sort(commits, key=key_function)  # 두 기준이 같은 정렬 알고리즘을 사용함.
        
        return True, result, f"Sorted by {option}"  # 정렬된 목록과 사용한 기준을 반환함.
