ARG SERVICE_NAME

FROM python:3

ENV SERVICE_NAME=profile

RUN mkdir -p /app
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY $SERVICE_NAME.py $SERVICE_NAME.py 
ENV FLASK_ENV development
ENV FLASK_APP /app/$SERVICE_NAME.py
ENV PYTHONPATH /app

EXPOSE 5000

ENTRYPOINT [ "python3" ]

CMD [ "/app/profile.py" ]
