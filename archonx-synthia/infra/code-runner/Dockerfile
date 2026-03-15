# Minimal sandbox — non-root, read-only FS, /work writable
FROM python:3.12-slim

# Create non-root user
RUN groupadd -r runner && useradd -r -g runner -d /home/runner -s /sbin/nologin runner

# Install minimal tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl jq git && \
    rm -rf /var/lib/apt/lists/*

# Install runner API dependencies
COPY requirements.txt /opt/runner/requirements.txt
RUN pip install --no-cache-dir -r /opt/runner/requirements.txt

COPY runner_api.py /opt/runner/runner_api.py

# Create writable work directory
RUN mkdir -p /work && chown runner:runner /work

USER runner
WORKDIR /work

EXPOSE 9000

CMD ["python", "/opt/runner/runner_api.py"]
