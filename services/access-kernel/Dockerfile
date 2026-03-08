FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app /app/app
COPY config /app/config

ENV ACCESS_KERNEL_DB_PATH=/data/access-kernel.db
ENV ACCESS_KERNEL_AUDIT_PATH=/data/audit.jsonl
ENV ACCESS_KERNEL_SECRETS_SCHEMA=/app/config/secrets-json-schema.json
ENV ACCESS_KERNEL_POLICY_PATH=/app/config/policy.json
ENV ACCESS_KERNEL_MASTER_KEY=

VOLUME ["/data"]
EXPOSE 8090

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8090"]
