FROM debian
MAINTAINER Stephen <stephenf@nero.net>

RUN apt-get update && apt-get -y dist-upgrade
RUN echo "deb http://ftp.debian.org/debian jessie-backports main" >> /etc/apt/sources.list.d/backports.list && \
    apt-get -y install build-essential cron python-dev python-pip libpq-dev librrd-dev && \
    apt-get clean

ADD . /root/netspryte/
RUN mkdir -p /var/lib/netspryte/data && \
    cd /root/netspryte && pip install $PWD

VOLUME /etc/netspryte /var/lib/netspryte/data

CMD ["/usr/sbin/cron", "-f"]
