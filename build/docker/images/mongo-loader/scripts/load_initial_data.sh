#!/bin/bash

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Constants
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

declare -r PROG=`basename $0`
declare -r PROG_NAME=`basename $0 .sh`
declare -r PROG_PATH=`eval realpath $(dirname $0)`

# return codes
declare -ri SUCCESS=0
declare -ri WARNING=1
declare -ri ERROR=2


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Functions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

function errMsg()
{
   echo -e "[${PROG}]: ERROR: $*" >&2
}


function advMsg()
{
   echo -e "[${PROG}]: ADVICE: $*" >&2
}


function usage()
{
   cat <<__CAT_EOF__
USAGE:
   ${PROG} <csvFilepath>

__CAT_EOF__
}


function checkEnvVars()
{
   # Check that needed environment variables are set
   for varName in "MONGO_HOST" "MONGO_PORT" "AUTHENTICATION_DATABASE" "USERNAME" "PASSWORD" "TARGET_DATABASE" "TARGET_COLLECTION"
   do
      [[ ! -v "${varName}" ]] && {
         errMsg "Environment variable not set: <${varName}>"
         advMsg "Please set this variable as an environment variable and try again."
         return ${ERROR}
      }
   done

   return ${SUCCESS}
}


function doImport()
{
   mongoimport \
      --host=${MONGO_HOST} \
      --port=${MONGO_PORT} \
      --authenticationDatabase=${AUTHENTICATION_DATABASE} \
      --username=${USERNAME} \
      --password=${PASSWORD} \
      --db=${TARGET_DATABASE} \
      --collection=${TARGET_COLLECTION} \
      --drop \
      --headerline \
      --file="${CSV_FILEPATH}" \
      --type=csv \
      --verbose ; retImport=$?


   return ${retImport}
}


function main()
{

   if [[ -z "${CSV_FILEPATH}" ]]; then
      errMsg "Argument not set: <csvFilepath>"
      echo ""
      usage
      return ${ERROR}
   fi

   checkEnvVars || return ${ERROR}

   return ${SUCCESS}
}


########################################################################################################################
#
# MAIN PROGRAM starts here...
#
########################################################################################################################

CSV_FILEPATH="$1"

main


