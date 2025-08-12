# Базовый образ Python
FROM python:3.11

RUN mkdir /askme-service

WORKDIR /askme-service

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "askme.wsgi"]
