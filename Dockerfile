FROM python:3.7.9-alpine3.12

RUN mkdir api
WORKDIR ./api
COPY . .

RUN apk update && apk add gcc libc-dev make git libffi-dev openssl-dev python3-dev libxml2-dev libxslt-dev tzdata

RUN pip3 install -r requirements.txt

EXPOSE 3005

CMD python3 app.py



