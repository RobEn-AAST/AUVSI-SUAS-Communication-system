FROM python:3.9

ENV PYTHONUNBUFFERED=1

ENV PROTOC_ZIP=protoc-3.13.0-linux-x86_64.zip

RUN apt-get update && apt-get install -y unzip

RUN curl -OL https://github.com/protocolbuffers/protobuf/releases/download/v3.13.0/$PROTOC_ZIP \
    && unzip -o $PROTOC_ZIP -d /usr/local bin/protoc \
    && unzip -o $PROTOC_ZIP -d /usr/local 'include/*' \ 
    && rm -f $PROTOC_ZIP

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1

RUN useradd -U -m interop

RUN usermod -aG sudo interop

RUN usermod --shell /bin/bash interop

RUN echo "interop:interop" | chpasswd

RUN echo "interop:interop" | chpasswd

WORKDIR /home/interop/

COPY interop-relay /home/interop/

RUN chown -R interop /home/interop

RUN python setup.py install

USER interop

RUN export PYTHONPATH=/usr/local/lib/python3.9/



