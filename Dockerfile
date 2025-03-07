FROM python:3.11

RUN apt-get update && \
    apt-get install -y etcd-client

COPY . /app
WORKDIR /app

RUN python -m venv /opt/venv
RUN /opt/venv/bin/pip install pip --upgrade && \
    /opt/venv/bin/pip install -r requirements.txt && \
    chmod +x entrypoint.sh

CMD ["/app/entrypoint.sh"]
