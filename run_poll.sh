#!/bin/bash

POLL_INTERVAL=${POLL_INTERVAL}

if [ "${POLL_INTERVAL}" == "" ];
then
  echo "ERROR: POLL_INTERVAL not set. Exiting."
  exit -1
fi

while true;
do
  python3 railtimes.py
  echo "Sleeping for ${POLL_INTERVAL}s..."
  sleep ${POLL_INTERVAL}
done
