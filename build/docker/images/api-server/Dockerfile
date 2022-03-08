FROM project3-ubuntu-python

RUN apt-get update \
      && apt-get dist-upgrade -y

COPY build/docker/images/api-server/api-server_requirements.txt /app/conf/
COPY src/api/ /app/src/api/

RUN python3 -m pip install --upgrade pip \
      && pip3 install --requirement /app/conf/api-server_requirements.txt

EXPOSE 5000

CMD [ "python3", "/app/src/api/main.py" ]
