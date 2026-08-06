FROM python:3.12-slim
WORKDIR /app
COPY rc_test/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY rc_test/test_server.py rc_test/test_client.py ./
COPY gen/python ./gen
ENV PYTHONPATH=/app/gen
ENV PYTHONUNBUFFERED=1
CMD ["python", "test_server.py"]
