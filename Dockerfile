FROM python:3.6-alpine

RUN apk update && apk add --upgrade --no-cache g++

RUN adduser -D trader

WORKDIR /home/trader

COPY trader trader
COPY tests tests
COPY requirements.txt requirements.txt
COPY manage.py manage.py
COPY run.py run.py

RUN python3.6 -m venv .env
RUN source .env/bin/activate
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN chown -R trader:trader ./
USER trader

RUN python manage.py -c config_dev.py -m migration db init
RUN python manage.py -c config_dev.py -m migration db migrate -m "Init migration"
RUN python manage.py -c config_dev.py -m migration db upgrade
RUN python manage.py -c config_dev.py -m migration add_root_user --login root --password r00tPWD#

EXPOSE 8080

ENTRYPOINT []
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "run:app", "--threads", "2", "--pid", "gunicorn.pid"]

# docker build -t trader:latest .
# docker run --name trader_dev -p 8888:8080 --rm trader:latest