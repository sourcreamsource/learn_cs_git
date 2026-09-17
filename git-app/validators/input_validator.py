# 타입 힌트를 위해 Optional, Tuple을 불러옴
from typing import Optional, Tuple
# 정렬 옵션 및 기본값 상수를 불러옴
from constants.git_constants import VALID_SORT_OPTIONS
# 에러 메시지 상수를 불러옴
from constants.messages import (
    # 이번 작업에 전달하거나 가져올 항목을 지정함.
    ERROR_EMPTY_BRANCH_NAME,
    # 이번 작업에 전달하거나 가져올 항목을 지정함.
    ERROR_EMPTY_COMMIT_MESSAGE,
    # 이번 작업에 전달하거나 가져올 항목을 지정함.
    ERROR_INVALID_ARGS,
# 앞에서 여러 줄로 적은 값이나 설정의 묶음을 마무리함.
)


# 사용자 입력값(문자열, 브랜치명, 커밋메시지 등)의 유효성을 검사하는 검증기 클래스임
class InputValidator:
    # 사용자명(Author)이 비어있지 않은지 검증하는 함수임
    @staticmethod
    # 아래 작업을 이름으로 다시 호출할 수 있게 함수로 정의함.
    def validate_author(author: Optional[str]) -> Tuple[bool, str]:
        # 문자열이 없거나 공백뿐인 경우 검증 실패 처리함
        if not author or not author.strip():
            # 처리 결과를 호출한 곳에 돌려주고 이 함수의 실행을 끝냄.
            return False, f"{ERROR_INVALID_ARGS}: author name is required"
        # 정상인 경우 공백이 정돈된 문자열 반환
        return True, author.strip()

    # 브랜치 이름의 유효성을 검사하는 함수임
    @staticmethod
    # 아래 작업을 이름으로 다시 호출할 수 있게 함수로 정의함.
    def validate_branch_name(branch_name: Optional[str]) -> Tuple[bool, str]:
        # 브랜치명이 비어있는 경우 실패 처리함
        if not branch_name or not branch_name.strip():
            # 처리 결과를 호출한 곳에 돌려주고 이 함수의 실행을 끝냄.
            return False, ERROR_EMPTY_BRANCH_NAME
        # 앞뒤 공백 제거
        cleaned = branch_name.strip()
        # 공백이 포함된 브랜치 이름 방지
        for character in cleaned:
            # 공백뿐 아니라 탭과 줄바꿈도 브랜치 이름에서 거부함.
            if character.isspace():
                # 공통 오류 접두사 뒤에 원인을 설명함.
                return False, "Invalid args: Branch name cannot contain spaces"
        # 처리 결과를 호출한 곳에 돌려주고 이 함수의 실행을 끝냄.
        return True, cleaned

    # 커밋 설명 메시지가 비어있지 않은지 검사하는 함수임
    @staticmethod
    # 아래 작업을 이름으로 다시 호출할 수 있게 함수로 정의함.
    def validate_commit_message(message: Optional[str]) -> Tuple[bool, str]:
        # 메시지가 없거나 공백뿐이면 에러 메시지 반환
        if not message or not message.strip():
            # 처리 결과를 호출한 곳에 돌려주고 이 함수의 실행을 끝냄.
            return False, ERROR_EMPTY_COMMIT_MESSAGE
        # 처리 결과를 호출한 곳에 돌려주고 이 함수의 실행을 끝냄.
        return True, message.strip()

    # 정렬 옵션 문자열이 유효한지 검사하는 함수임 (date 또는 author)
    @staticmethod
    # 아래 작업을 이름으로 다시 호출할 수 있게 함수로 정의함.
    def validate_sort_option(sort_by: Optional[str]) -> Tuple[bool, str]:
        # 정렬 기준 문자열이 없으면 기본값인 date로 설정함
        if sort_by is None:
            # 처리 결과를 호출한 곳에 돌려주고 이 함수의 실행을 끝냄.
            return True, "date"
        # 다음 단계에서 쓸 값을 계산하거나 꺼내 변수에 보관함.
        cleaned = sort_by.strip().lower()
        # 허용된 옵션 목록에 포함되는지 검사함
        if cleaned not in VALID_SORT_OPTIONS:
            # 처리 결과를 호출한 곳에 돌려주고 이 함수의 실행을 끝냄.
            return False, f"Invalid args: Invalid sort option: {sort_by}"
        # 처리 결과를 호출한 곳에 돌려주고 이 함수의 실행을 끝냄.
        return True, cleaned
