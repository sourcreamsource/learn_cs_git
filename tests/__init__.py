# 시스템 파일 및 디렉토리 경로 설정을 위해 os 모듈을 불러옴
import os
# 파이썬 런타임 시스템 모듈을 불러옴
import sys

# 프로젝트 루트 디렉토리 경로를 계산함
_proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# git-app 디렉토리 경로를 계산함
_git_app_dir = os.path.join(_proj_root, "git-app")

# 파이썬 모듈 검색 경로 최우선 순위로 git-app 디렉토리를 등록함
if _git_app_dir not in sys.path:
    sys.path.insert(0, _git_app_dir)
