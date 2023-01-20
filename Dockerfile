FROM abhinavsingh/proxy.py:latest

RUN apk update && apk add openssl
RUN pip install redis