FROM debian
MAINTAINER Stephen <stephenf@nero.net>

RUN apt-get update && apt-get -y dist-upgrade
RUN echo "deb http://ftp.debian.org/debian jessie-backports main" >> /etc/apt/sources.list.d/backports.list && \
    apt-get -y install nginx uwsgi uwsgi-plugin-python supervisor \
    build-essential python-dev python-pip libpq-dev librrd-dev && \
    apt-get clean

RUN echo "daemon off;" >> /etc/nginx/nginx.conf
COPY docker/web/supervisor-netspryte.conf /etc/supervisor/conf.d/
COPY docker/web/nginx-netspryte.conf /etc/nginx/sites-available/default

ADD . /root/netspryte/
RUN mkdir -p /var/lib/netspryte/data && \
    cd /root/netspryte && pip install $PWD

EXPOSE 80
VOLUME /etc/netspryte /var/lib/netspryte/data

CMD ["/usr/bin/supervisord", "-n"]
