#!/bin/sh

if [ -z "${CAF_APP_CONFIG_FILE}" ]; then
    echo "CAF_APP_CONFIG_FILE is not set" >&2
    exit 1
fi

if [ ! -f "${CAF_APP_CONFIG_FILE}" ]; then
    echo "CAF_APP_CONFIG_FILE does not exist: ${CAF_APP_CONFIG_FILE}" >&2
    exit 1
fi

for line in $(grep -v '\[mainconfig\]' "${CAF_APP_CONFIG_FILE}" | sed -e 's/ = /=/' | grep -v '^$'); do
    key=$(echo "$line" | cut -d'=' -f1)
    value=$(echo "$line" | cut -d'=' -f2-)
    if ! env | grep -q "^${key}="; then
        export "${key}=${value}"
    fi
done

while [ 1 ]
do
    python3 /main.py
    sleep 10
done
