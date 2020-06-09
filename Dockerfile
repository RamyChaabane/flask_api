FROM python:2.7

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

RUN mkdir -p /home/flask
    && groupadd flask
    && useradd -g flask flask -d /home/flask
WORKDIR /home/flask
USER flask

COPY . .

ENV FLASK_ENV development

CMD [ "python", "run.py" ]
