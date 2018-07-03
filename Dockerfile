# MULTISITE CONTAINER
#
# DOCKER RUN ARGS
# --network=web
# --volume=/root/_flexx/apps:/root/flexx_apps
# --memory="256m"
# --cpus="0.5"
# --label="traefik.docker.network=web"
# --label="traefik.enable=true"
# --label="traefik.flexxapp.frontend.rule=Host:flexx.app"
# --label="traefik.flexxapp.protocol=http"
# --label="traefik.flexxapp.port=80"
# --label="traefik.flexxlive.frontend.rule=Host:flexx.live,www.flexx.live"
# --label="traefik.flexxlive.protocol=http"
# --label="traefik.flexxlive.port=80"

FROM python:3.6-alpine

RUN apk add --no-cache gcc g++ make linux-headers musl-dev libffi-dev openssl-dev git \
    && pip --no-cache-dir install psutil cffi jwt markdown cchardet aiodns uvloop aiohttp


WORKDIR /root
COPY . .

CMD python server.py --host=0.0.0.0 --port=80 --appdir=/root/flexx_apps
