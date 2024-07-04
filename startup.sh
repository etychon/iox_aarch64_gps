#!/bin/sh

for line in `grep -v '\[mainconfig\]' ${CAF_APP_CONFIG_FILE} | sed -e 's/ = /=/' | grep -v '^$'`;
do
        key=$(echo "$line" | cut -d'=' -f1)
        if ! env | grep -q "^$key="; then
                export $line;
	fi
done

while [ 1 ]
do
    # start the main script
    python3 /main.py
    # if script fails or exit, wait 10 second, try again.
    sleep 10
done
