#
# Dockerfile: mongo-client
#
FROM project3-ubuntu-python

COPY build/docker/images/mongo-client/python_requirements.txt /app/conf/

RUN python3 -m pip install --upgrade pip \
      && pip3 install --requirement /app/conf/python_requirements.txt
