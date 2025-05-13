FROM python:3.10-slim

WORKDIR /app

# UV 설치
RUN pip install uv

# UV로 패키지 설치 (--system 옵션 추가)
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# 소스 코드 복사
COPY . .

# UV로 서버 실행
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8090"]