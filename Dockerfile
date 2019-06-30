FROM python:3.7.3-alpine

COPY . /usr/src/currency_converter_api
WORKDIR /usr/src/currency_converter_api

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

ENV CORES_NUM=4
CMD /usr/local/bin/gunicorn -w $(($CORES_NUM * 2 + 1)) -b :8000 "api:create_app()"