FROM python:3

RUN mkdir app

COPY config.yml /app
COPY TrackController.py /app

ENTRYPOINT ["python", "/app/TrackController.py"]