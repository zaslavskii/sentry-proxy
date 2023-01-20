import gzip
import time
from typing import Optional

from redis import Redis

from proxy.http.exception import HttpRequestRejected
from proxy.http.parser import HttpParser
from proxy.http.proxy import HttpProxyBasePlugin

TTL = 30
RATE = 10
REDIS = Redis(host='redis')


class SentryPlugin(HttpProxyBasePlugin):
    """Modify POST request body before sending to upstream server.

    Following curl executions will work:
        1. Plain
           curl -v -x localhost:8899 -X POST http://httpbin.org/post -d 'key=value'
        2. Chunked
           curl -v -x localhost:8899 -X POST \
               -H 'Transfer-Encoding: chunked' http://httpbin.org/post -d 'key=value'
        3. Chunked & Compressed
           echo 'key=value' | gzip | curl -v \
               -x localhost:8899 \
               -X POST \
               --data-binary @- -H 'Transfer-Encoding: chunked' \
               -H 'Content-Encoding: gzip' http://httpbin.org/post

    """

    def handle_client_request(
            self, request: HttpParser,
    ) -> Optional[HttpParser]:
        data = request.body
        if self.__is_gzip(request):
            data = gzip.decompress(data)

        curr = int(time.time() / TTL)
        counter = REDIS.incr(str(curr), 1)
        REDIS.expire(str(curr), TTL + 5, True)

        if counter >= RATE:
            raise HttpRequestRejected(
                status_code=429,
                reason=b'Too many errors of this type',
            )

        return request

    def __is_gzip(self, request: HttpParser) -> bool:
        return request.has_header(b'content-encoding') and request.header(
            b'content-encoding') == b'gzip'

    def __is_json(self, request: HttpParser) -> bool:
        return request.has_header(b'content-type') and request.header(
            b'content-type') == b'application/json'
