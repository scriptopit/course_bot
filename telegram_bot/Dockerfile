FROM python:3.10-alpine

WORKDIR /app

COPY requirements.txt .

RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

CMD ["python", "main.py"]
