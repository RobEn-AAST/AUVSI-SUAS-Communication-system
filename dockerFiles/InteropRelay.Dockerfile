FROM python:3.9

ENV PYTHONUNBUFFERED=1

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1

RUN pip install LatLon

RUN pip install future

RUN pip install lxml

RUN pip install nose

RUN pip install protobuf==3.20

RUN pip install pymavlink==2.4.14

RUN pip install pyserial

RUN pip install requests

COPY protoc-binaries/bin/protoc  /usr/local/bin/protoc

COPY protoc-binaries/include/* /usr/local/include/*

WORKDIR /home/interop/

COPY interop-relay /home/interop/

RUN python setup.py install

RUN useradd -U -m interop

RUN usermod -aG sudo interop

RUN usermod --shell /bin/bash interop

RUN echo "interop:interop" | chpasswd

RUN echo "interop:interop" | chpasswd

RUN chown -R interop /home/interop

USER interop

RUN export PYTHONPATH=/usr/local/lib/python3.9/