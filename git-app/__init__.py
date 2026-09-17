# 시스템 및 경로 설정을 다루기 위해 os 모듈을 불러옴
import os
# 파이썬 시스템 모듈을 불러옴
import sys

# 현재 git-app 디렉토리를 파이썬 검색 경로에 최우선으로 등록하여 내부 모듈 임포트를 원활하게 함
_current_dir = os.path.dirname(os.path.abspath(__file__))
# 검색 경로에 아직 없다면 맨 앞에 삽입함
if _current_dir not in sys.path:
    # 준비한 값으로 이 단계의 작업을 실행함.
    sys.path.insert(0, _current_dir)
