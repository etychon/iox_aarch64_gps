FROM arm64v8/alpine:3.21 AS build-stage

LABEL org.opencontainers.image.version="0.10"

COPY requirements.txt /requirements.txt

RUN apk add --no-cache python3 py3-pip && \
    python3 -m venv /venv && \
    /venv/bin/pip install --no-cache-dir -r /requirements.txt && \
    mkdir -p /python_pkgs && \
    cp -a /venv/lib/python3.*/site-packages/. /python_pkgs/

FROM arm64v8/alpine:3.21 AS prod-stage

LABEL org.opencontainers.image.version="0.10"

RUN apk add --no-cache python3

ENV PYTHONPATH=/python_pkgs

COPY --from=build-stage /python_pkgs /python_pkgs

COPY startup.sh /startup.sh
RUN chmod 755 /startup.sh

COPY main.py /main.py
RUN chmod 755 /main.py

CMD ["/bin/sh", "/startup.sh"]
