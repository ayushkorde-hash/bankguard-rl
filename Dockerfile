FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir openenv-core || pip install --no-cache-dir openenv || echo "openenv install attempted"

COPY . .

RUN pip install --no-cache-dir -e . || true

EXPOSE 7860

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]