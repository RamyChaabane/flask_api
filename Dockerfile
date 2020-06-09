FROM python:2.7

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

COPY . .

ENV FLASK_ENV development

CMD [ "python", "run.py" ]
