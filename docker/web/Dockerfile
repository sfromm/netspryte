FROM sfromm/baseimage
MAINTAINER Stephen <stephenf@nero.net>

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get -y --no-install-recommends install nginx uwsgi uwsgi-plugin-python libpq-dev librrd-dev && \
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
