FROM python:3.9-slim-buster AS base
WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
FROM base AS production
COPY . .
CMD ["python3", "main.py","0.0.0.0","5000"]
