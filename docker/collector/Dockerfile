FROM sfromm/baseimage
MAINTAINER Stephen <stephenf@nero.net>

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
    apt-get -y --no-install-recommends install build-essential libpq-dev librrd-dev && \
    apt-get clean

ADD . /root/netspryte/
RUN mkdir -p /var/lib/netspryte/data && \
    cd /root/netspryte && pip install $PWD

VOLUME /etc/netspryte /var/lib/netspryte/data

CMD ["/usr/sbin/cron", "-f"]
