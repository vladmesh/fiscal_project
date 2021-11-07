FROM ubuntu:18.04

RUN apt update -y
RUN apt install -y curl python3.8 python3-pip python3.8-dev python3.8-venv
RUN ln -s /usr/bin/python3.8 /usr/bin/python & \
    ln -s /usr/bin/pip3 /usr/bin/pip
RUN python -m venv /venv
ENV PATH=/venv/bin:$PATH
RUN pip install wheel
COPY requirements.txt .
RUN pip install -r requirements.txt