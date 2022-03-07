#!/bin/bash

declare CONTAINER_CSV_FILEPATH="$1"

mongoimport \
   --host=\"${MONGO_HOST}\"                         \
   --port=\"${MONGO_PORT}\"                         \
   --authenticationDatabase=\"${MONGO_AUTHENT_DB}\" \
   --username=\"${MONGO_USER}\"                     \
   --password=\"${MONGO_PWD}\"                      \
   --db=\"${TARGET_DATABASE}\"                      \
   --collection=\"${TARGET_COLLECTION}\"            \
   --drop                                           \
   --headerline                                     \
   --file=\"${CONTAINER_CSV_FILEPATH}\"             \
   --type=csv                                       \
   --verbose                                        \
   2>&1 | tee /app/log/initial_import.log
ret=$?

echo "[RC=${ret}]"

exit ${ret}