FROM alpine:latest

ENV PYTHONUNBUFFERED=1

RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python

RUN apk add py3-numpy

RUN python3 -m ensurepip

RUN pip3 install --no-cache --upgrade pip setuptools

RUN apk add dpkg

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1

RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

RUN apk add build-base

RUN apk add python3-dev

# Alpine cleanup
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h
# -- Hack because the function prototype doesn't match expected
RUN sed -i 's/, int,/, unsigned int,/' /usr/include/assert.h

RUN pip install numpy

RUN pip install mavproxy

RUN apk add sudo bash shadow

RUN useradd -U -m mavproxy

RUN usermod -aG wheel mavproxy

RUN usermod --shell /bin/bash mavproxy

RUN echo "mavproxy:mavproxy" | chpasswd

RUN echo "mavproxy:mavproxy" | chpasswd

WORKDIR /home/mavproxy/

RUN chown -R mavproxy /home/mavproxy

USER mavproxy