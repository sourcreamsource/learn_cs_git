# inverted_index.py — 역색인 클래스 구현

# 타입 힌트를 위해 Dict, List를 불러옴
from typing import Dict, List


# 키워드 및 작성자 정보를 키로 삼아 커밋 목록을 O(1)에 바로 찾는 역색인(Inverted Index) 클래스임
class InvertedIndex:
    # 키워드 색인과 작성자 색인 딕셔너리를 초기화하는 생성자 함수임
    def __init__(self) -> None:
        
        # ✅ 키워드 색인 
        # 단어(토큰)를 키로 하고 커밋 번호 사전을 값으로 갖는 역색인 맵임 (예: {"login": {"a1b2c3": None}})
        self._keyword_index: Dict[str, Dict[str, None]] = {}
        
        # ```python
        # ❤️ 구조: {단어: [커밋해시들]}
        # keyword_index = {
        #     "로그인": ["a1b2c3", "d4e5f6"],
        #     "기능": ["a1b2c3", "g7h8i9"],
        #     "버튼": ["d4e5f6"],
        #     "추가": ["a1b2c3", "g7h8i9", "j1k2l3"],
        # }

        # ❤️ 검색: O(1) 조회
        # def search_keyword(index, word):
        #     return index.get(word.lower(), [])
        # ```                
        

        # ✅ 작성자 색인
        # 작성자 이름을 키로 하고 커밋 번호 사전을 값으로 갖는 역색인 맵임 (예: {"alice": {"a1b2c3": None}})
        self._author_index: Dict[str, Dict[str, None]] = {}
        
        # ```python
        # ❤️ 구조: {작성자: [커밋해시들]}  
        # author_index = {  
        #     "홍길동": ["a1b2c3", "d4e5f6", "g7h8i9"],  
        #     "김철수": ["j1k2l3", "m4n5o6"],  
        # }  

        # ❤️ 검색: O(1) 조회  
        # def search_author(index, name):  
        #     return index.get(name, [])  
        # ```



    # ✅ 커밋 메시지에서 단어를 추출하여 소문자로 정규화하는 헬퍼 함수
    def tokenize(self, text: str) -> List[str]:
        
        # 문자열 양쪽 공백을 제거하고 모두 소문자로 변환함
        normalized = text.strip().lower()
        
        # 공백 문자를 기준으로 문자열을 단어 단위로 쪼개어 리스트로 만듦
        tokens = normalized.split()
        # 정규화된 단어 토큰 리스트를 반환함
        
        return tokens


    # ✅ 커밋 즉시 바로 키워드 및 작성자 역색인 추가
    # 새로운 커밋이 생성될 때 역색인에 즉시 등록하는 갱신 함수임 (평가항목 2, 3: 실시간 동기화)
    def add_commit(self, commit_hash: str, message: str, author: str) -> None:
        
        # ❤️  1. 작성자 색인 갱신: 대소문자를 통일하여 어떤 입력 형태도 같은 서랍에서 찾게 함
        cleaned_author = author.strip().lower()
        # 해당 작성자가 색인 맵에 아직 등록되지 않았다면 빈 사전을 만듦
        if cleaned_author not in self._author_index:
            # 다른 메서드에서도 사용할 수 있도록 객체 안에 보관함.
            self._author_index[cleaned_author] = {}
        # 중복 등록을 방지하기 위해 아직 커밋 해시가 없으면 추가함
        if commit_hash not in self._author_index[cleaned_author]:
            # 다른 메서드에서도 사용할 수 있도록 객체 안에 보관함.
            self._author_index[cleaned_author][commit_hash] = None

        # ❤️ 2. 키워드 색인 갱신: 메시지에서 소문자 단어 토큰들을 추출함
        tokens = self.tokenize(message)
        # 추출한 각 단어를 순회함
        for token in tokens:
            # 단어가 키워드 색인 맵에 없으면 빈 사전을 등록함
            if token not in self._keyword_index:
                # 다른 메서드에서도 사용할 수 있도록 객체 안에 보관함.
                self._keyword_index[token] = {}
            # 해당 단어의 커밋 목록에 중복 없이 커밋 해시를 추가함
            if commit_hash not in self._keyword_index[token]:
                # 다른 메서드에서도 사용할 수 있도록 객체 안에 보관함.
                self._keyword_index[token][commit_hash] = None


    # ✅ ❤️ 키워드 역색인 검색
    # 단어 후보를 평균 O(1)에 찾고 결과 K개를 꺼내는 함수임
    def search_by_keyword(self, keyword: str) -> List[str]:
        # 검색어를 커밋 메시지와 같은 규칙으로 단어 목록으로 나눔
        query_tokens = self.tokenize(keyword)
        # 빈 검색어는 찾을 단어가 없으므로 빈 목록을 반환함
        if not query_tokens:
            # 처리 결과를 호출한 곳에 돌려주고 이 함수의 실행을 끝냄.
            return []

        # 첫 단어의 색인 목록을 후보로 가져옴
        first_token = query_tokens[0]
        # 다음 단계에서 쓸 값을 계산하거나 꺼내 변수에 보관함.
        candidate_hashes = self._keyword_index.get(first_token, {})
        # 후보가 적은 단어부터 확인하면 불필요한 검사가 줄어듦.
        for token in query_tokens:
            # 단어별 번호 사전을 가져옴.
            token_hashes = self._keyword_index.get(token, {})
            # 더 작은 후보 바구니를 골라 사용함.
            if len(token_hashes) < len(candidate_hashes):
                # 사전의 입력 순서는 커밋 등록 순서를 유지함.
                candidate_hashes = token_hashes
        # 여러 단어 검색 결과를 담을 빈 목록을 준비함
        matched_hashes: List[str] = []

        # 후보 단어를 가진 커밋만 확인하므로 전체 커밋을 순회하지 않음
        for commit_hash in candidate_hashes:
            # 모든 검색 단어가 이 커밋의 색인에 들어 있는지 나타내는 표시임
            contains_all_tokens = True
            # 검색어의 모든 단어가 있는지 검사함
            for token in query_tokens:
                # 현재 단어의 색인 목록을 가져오며 없으면 빈 사전으로 처리함
                token_hashes = self._keyword_index.get(token, {})
                # 현재 커밋에 이 단어가 없으면 여러 단어 조건을 만족하지 못함
                if commit_hash not in token_hashes:
                    # 다음 단계에서 쓸 값을 계산하거나 꺼내 변수에 보관함.
                    contains_all_tokens = False
                    # 더 확인할 필요가 없으므로 단어 검사 반복을 끝냄
                    break

            # 모든 검색 단어가 들어 있는 커밋만 결과에 추가함
            if contains_all_tokens:
                # 찾은 항목을 목록 끝에 추가하여 기억함.
                matched_hashes.append(commit_hash)

        # 원본 색인 목록을 건드리지 않는 새 결과 목록을 반환함
        return matched_hashes


    # ✅ ❤️ 작성자 역색인 검색
    # 작성자 후보를 평균 O(1)에 찾고 K개 번호를 복사하는 함수임
    def search_by_author(self, author: str) -> List[str]:
        # 검색할 작성자 이름을 등록할 때와 같은 규칙으로 소문자 정규화함
        cleaned_author = author.strip().lower()
        # 작성자 이름을 키로 즉시 색인 목록의 복사본을 반환하며 없으면 빈 목록을 반환함
        return list(self._author_index.get(cleaned_author, []))



    # ✅ 
    # 역색인 내의 모든 데이터를 비우는 함수임
    def clear(self) -> None:
        # 키워드 색인 맵 비우기
        self._keyword_index.clear()
        # 작성자 색인 맵 비우기
        self._author_index.clear()
