#!/bin/bash

POLLING_INTERVAL=120

cd /apps/nationalrail

while true;
do
  python3 railtimes.py
  echo "Sleeping for ${POLLING_INTERVAL}s..."
  sleep ${POLLING_INTERVAL}
done
