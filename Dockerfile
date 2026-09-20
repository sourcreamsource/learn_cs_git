# 파이썬 3.11 슬림 이미지를 기반으로 설정함
FROM python:3.11-slim

# 컨테이너 내 작업 디렉토리를 /app으로 지정함
WORKDIR /app

# 실행에 필요한 소스만 복사하여 환경 파일이나 개인 문서가 들어가지 않게 함.
COPY git-app/ /app/git-app/

# 이미지 안에서도 동작을 확인할 수 있도록 비밀값 없는 테스트만 복사함.
COPY tests/ /app/tests/

# 표준 출력이 지연 없이 즉시 터미널에 나타나도록 환경변수 설정함
ENV PYTHONUNBUFFERED=1

# 캐시 파일을 만들지 않아 읽기 전용 소스 연결에서도 실행할 수 있게 함.
ENV PYTHONDONTWRITEBYTECODE=1

# 외부 패키지가 없으므로 이미지에 들어 있는 파이썬으로 바로 실행함.
CMD ["python", "-m", "git-app"]
