#
# Dockerfile: mongo-client
#
FROM project3-ubuntu-python

COPY python_requirements.txt /app/conf/

RUN python3 -m pip install --upgrade pip \
      && pip3 install --requirement /app/conf/python_requirements.txt

