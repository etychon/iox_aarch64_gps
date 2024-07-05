FROM arm64v8/alpine:3.15 AS build-stage

COPY requirements.txt /requirements.txt

RUN	apk update && \
    	apk add python3 py3-pip && \
	pip3 install -r requirements.txt && \
	rm -rf /usr/lib/python3.9/site-packages/pip*

FROM arm64v8/alpine:3.15 AS prod-stage

RUN     apk update && \
        apk add --no-cache python3

COPY --from=build-stage /usr/lib/python3.9/site-packages /usr/lib/python3.9/site-packages

COPY startup.sh /startup.sh
RUN chmod 755 /startup.sh

COPY main.py /main.py
RUN chmod 755 /main.py

CMD ". ./startup.sh"
