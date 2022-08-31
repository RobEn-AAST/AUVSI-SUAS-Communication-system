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

RUN pip install empy

RUN pip install requests

RUN pip install dronekit

RUN pip install flask

RUN apt update -y && apt install -y libopencv-dev python3-opencv && pip install opencv-python

COPY protoc-binaries/bin/protoc  /usr/local/bin/protoc

COPY protoc-binaries/include/* /usr/local/include/*

WORKDIR /home/proxyServer/

COPY proxyServer /home/proxyServer/

RUN python setup.py install

RUN useradd -U -m proxyServer

RUN usermod -aG sudo proxyServer

RUN usermod --shell /bin/bash proxyServer

RUN echo "proxyServer:proxyServer" | chpasswd

RUN echo "proxyServer:proxyServer" | chpasswd

RUN chown -R proxyServer /home/proxyServer

USER proxyServer

RUN export PYTHONPATH=/usr/local/lib/python3.9/