FROM python:3.9

WORKDIR /app

RUN apt-get update && apt-get install -y cron && apt-get clean

COPY requirements.txt .
COPY extract.py .
COPY transform.py .
COPY load.py .

COPY main.py .
COPY run_etl.sh .


RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x /app/run_etl.sh


ENV DB_USER=myuser
ENV DB_PASS=mypassword
ENV DB_HOST=db
ENV DB_NAME=mydatabase

ENV MOOVITAMIX_API_URL=http://localhost:8000

RUN touch /var/log/cron.log

RUN echo "0 0 * * * /app/run_etl.sh >> /var/log/cron.log 2>&1" >> /etc/cron.d/etl-cron-job

# Apply cron job and give cron permission to run
RUN chmod 0644 /etc/cron.d/etl-cron-job
RUN crontab /etc/cron.d/etl-cron-job

# Start cron in the background and also keep the container running
CMD cron && tail -f /var/log/cron.log
