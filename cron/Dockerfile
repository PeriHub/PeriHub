FROM alpine:edge

LABEL maintainer="Jan-Timo Hesse <jan-timo.hesse@dlr.de>"

RUN apk update && apk add curl
ADD crontab /crontab
ADD script.sh /script.sh
COPY entry.sh /entry.sh
RUN chmod 755 /script.sh /entry.sh
RUN /usr/bin/crontab crontab

CMD ["/entry.sh"]