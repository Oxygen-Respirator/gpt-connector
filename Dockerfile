# 베이스 이미지 선택 (Python 3.9)
FROM python:3.9

# 환경변수 설정 (Python 출력을 버퍼링하지 않음)
ENV PYTHONUNBUFFERED=1

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 파일을 컨테이너에 복사
COPY requirements.txt .

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트의 모든 파일을 컨테이너에 복사
COPY . .

# run.sh에 실행 권한 부여
RUN chmod +x run.sh