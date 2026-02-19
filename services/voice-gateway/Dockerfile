FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app /app/app
ENV ACCESS_KERNEL_BASE_URL=http://access-kernel:8090
ENV VOICE_ALLOWLIST=+15550000001
ENV VOICE_PASSPHRASE=archonx-passphrase
ENV VOICE_PIN=1234
ENV VOICE_MAX_ATTEMPTS=5
ENV VOICE_LOCKOUT_SECONDS=300
ENV VOICE_STORE_TRANSCRIPTS=false

EXPOSE 8091
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8091"]
