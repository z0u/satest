FROM ubuntu:14.04

MAINTAINER Alex Fraser <alex@vpac-innovations.com.au>

RUN DEBIAN_FRONTEND=noninteractive \
    apt-get update && \
    apt-get install -y \
        build-essential \
        python3 \
        python3.4-dev \
        python3-pip \
        --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install -vU setuptools

COPY requirements.txt /tmp/
WORKDIR /tmp
RUN pip3 install -r requirements.txt

COPY ./ /root/satest
WORKDIR /root/satest

CMD ["python3", "-m", "unittest", "discover"]
