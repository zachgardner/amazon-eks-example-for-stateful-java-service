FROM python:3

ENV SERVICE_NAME=leaderboard

RUN mkdir -p /app
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY $SERVICE_NAME.py $SERVICE_NAME.py 
ENV FLASK_ENV development
ENV FLASK_APP /app/$SERVICE_NAME.py
ENV PYTHONPATH /app
EXPOSE 5000

CMD [ "flask", "run", "--host=0.0.0.0" ]
