FROM python:3.13-slim

WORKDIR /app

COPY requirements/extract.txt requirements/extract.txt
RUN pip install --no-cache-dir -r requirements/extract.txt

COPY . .

ENTRYPOINT ["python", "src/Extract/main_extract.py"]