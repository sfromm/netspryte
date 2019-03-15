FROM sfromm/baseimage
MAINTAINER Stephen <stephenf@nero.net>

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
    apt-get -y --no-install-recommends install nginx uwsgi uwsgi-plugin-python3 build-essential libpq-dev librrd-dev && \
    apt-get clean

RUN echo "daemon off;" >> /etc/nginx/nginx.conf && \
    mkdir /etc/service/nginx /etc/service/uwsgi

ADD docker/web/nginx-netspryte.conf /etc/nginx/sites-available/default
ADD docker/web/nginx.runit /etc/service/nginx/run
ADD docker/web/uwsgi.runit /etc/service/uwsgi/run

ADD . /root/netspryte/
RUN mkdir -p /var/lib/netspryte/data && \
    cd /root/netspryte && pip3 install $PWD

EXPOSE 80
VOLUME /etc/netspryte /var/lib/netspryte/data

CMD ["/sbin/my_init"]
