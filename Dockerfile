FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY test/ test/
COPY run_pipeline.sh .

# Make the script executable
# This sometimes has weird issues because of how container copies permissions
RUN chmod +x run_pipeline.sh
RUN mkdir -p data logs

ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["./run_pipeline.sh"] 