FROM python:latest

COPY . /srv

WORKDIR /srv

ARG DEBIAN_FRONTEND="noninteractive"
ENV TZ=Australia/Sydney

RUN apt-get update && \
    apt-get dist-upgrade -y && \
    apt-get install -y cron supervisor

RUN pip install -r requirements.txt

RUN crontab /srv/crontab.txt

RUN chmod 600 /etc/crontab

EXPOSE 5000/tcp

CMD ["supervisord","-c","/srv/supervisor.conf"]
