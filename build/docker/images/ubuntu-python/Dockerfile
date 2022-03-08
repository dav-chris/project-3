#
# Dockerfile: ubuntu-python
#
FROM ubuntu:latest

ENV PYTHON_VERSION="3.8.5"

RUN apt-get update \
   && apt-get dist-upgrade -y

RUN DEBIAN_FRONTEND=noninteractive TZ=Europe/Paris apt-get -y install tzdata

RUN apt-get install -y \
         wget            \
         build-essential gdb lcov pkg-config \
         libbz2-dev libffi-dev libgdbm-dev libgdbm-compat-dev liblzma-dev \
         libncurses5-dev libreadline6-dev libsqlite3-dev libssl-dev \
         lzma lzma-dev tk-dev uuid-dev zlib1g-dev

RUN  cd /usr/local/src \
      && wget http://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz \
      && tar -xvzf Python-${PYTHON_VERSION}.tgz \
      && cd Python-${PYTHON_VERSION} \
      && ./configure --enable-optimizations --with-ensurepip=install \
      && make \
      && make install
