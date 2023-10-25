FROM python:3.9.10-buster

EXPOSE 5000

RUN apt-get update && \
  apt-get install --yes --no-install-recommends chromium

RUN pip install --upgrade pip
RUN pip install --no-cache-dir gunicorn

ARG uid=1000
ARG gid=1000

RUN groupadd -g ${gid} validata && \
  useradd -u ${uid} -g ${gid} --create-home --shell /bin/bash validata

ADD nginx.conf.sigil /home/validata/

# Cf https://bugs.chromium.org/p/chromium/issues/detail?id=638180 and https://blog.ineat-conseil.fr/2018/08/executer-karma-avec-chromeheadless-dans-un-conteneur-docker/
USER validata

WORKDIR /home/validata/

COPY --chown=validata:validata requirements.txt .
COPY --chown=validata:validata config.yaml .
RUN pip install --no-cache-dir -r requirements.txt --no-warn-script-location

CMD gunicorn --workers 4 --bind 0.0.0.0:5000 validata_ui:app
