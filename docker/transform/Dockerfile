FROM python:3.13-slim

WORKDIR /app

COPY requirements/transform.txt requirements/transform.txt
RUN pip install --no-cache-dir -r requirements/transform.txt

COPY . .

ENTRYPOINT ["python", "src/Transform/main_transform.py"]