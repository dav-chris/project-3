#
# Dockerfile: mongo-loader
#
FROM project3-mongo-client



ARG CSV_FILENAME=data.csv

COPY data/${CSV_FILENAME} /app/data/data.csv

COPY src/mongo-loader/ /app/src/

COPY build/docker/images/mongo-loader/conf/ /app/src/conf/

VOLUME ["/app/log"]

WORKDIR "/app/src"

#CMD [ "python3"               \
#   ,  "main.py"               \
#   ,  "/app/data/data.csv"    \
#]

CMD python3 main.py /app/data/data.csv > /app/log/log.txt 2>&1