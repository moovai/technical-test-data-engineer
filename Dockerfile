FROM python:3.11-slim

WORKDIR /app

# Copy all files (app.py, scripts/, requirements.txt)
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "src.moovitamix_fastapi.main:app", "--host", "0.0.0.0", "--port", "8000"]