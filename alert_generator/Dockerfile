FROM python:3.8-slim-buster

WORKDIR /app

COPY ./requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
COPY ./utils/. ./utils/.
COPY ./alert_generator/. .
CMD ["python3", "alert_generator.py"]
