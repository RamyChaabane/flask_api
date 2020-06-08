FROM python:2.7

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

USER useradd --create-home flask
WORKDIR /home/flask
USER flask

COPY . .

ENV FLASK_APP=api.py FLASK_ENV=development

CMD [ "python", "./api.py" ]
