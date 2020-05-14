# mypaas.service = flexx.app
# mypaas.url = https://flexx.app
#
# mypaas.scale = 0
# mypaas.maxmem = 256m
# mypaas.volume = /root/_flexx/apps:/root/flexx_apps

FROM python:3.8-slim-buster

RUN pip --no-cache-dir install aiohttp


WORKDIR /root
COPY . .

CMD ["python", "server.py", "host=0.0.0.0", "port=80", "appdir=/root/flexx_apps"]
