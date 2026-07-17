FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install chromium
RUN playwright install-deps chromium

CMD ["gunicorn", "relatorio_generator:app", "--bind", "0.0.0.0:10000"]
