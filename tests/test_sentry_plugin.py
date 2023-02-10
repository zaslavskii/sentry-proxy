from pathlib import Path
from tempfile import NamedTemporaryFile

from proxy import TestCase
from proxy.common.constants import DEFAULT_CLIENT_RECVBUF_SIZE
from proxy.common.utils import socket_connection
from proxy.http.responses import NOT_FOUND_RESPONSE_PKT

from tests.conftest import zero_division_error_request


class TestSentryPlugin(TestCase):
    PROXY_PY_STARTUP_FLAGS = TestCase.DEFAULT_PROXY_PY_STARTUP_FLAGS + [
        "--enable-web-server",
        "--plugins",
        "sentry_proxy.SentryPlugin",
    ]
    LOGS_FILE_PATH = None

    @classmethod
    def setUpClass(cls) -> None:
        tmp_file = NamedTemporaryFile(delete=False)
        tmp_file.close()
        cls.LOGS_FILE_PATH = Path(tmp_file.name)
        cls.PROXY_PY_STARTUP_FLAGS.append("--log-file")
        cls.PROXY_PY_STARTUP_FLAGS.append(str(cls.LOGS_FILE_PATH.absolute()))
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        print("=================================")
        print("==========LOGS FROM PROXY========")
        print("=================================")
        print(cls.LOGS_FILE_PATH.read_text())
        print("=================================")
        print("=================================")
        cls.LOGS_FILE_PATH.unlink()

    def __test(self):
        with socket_connection(("localhost", self.PROXY.flags.port)) as conn:
            conn.send(
                zero_division_error_request(
                    url=b"http://localhost:%d/" % self.PROXY.flags.port,
                    headers={
                        b"Host": b"localhost:%d" % self.PROXY.flags.port,
                    },
                )
            )
            response = conn.recv(DEFAULT_CLIENT_RECVBUF_SIZE)
        self.assertEqual(
            response,
            NOT_FOUND_RESPONSE_PKT.tobytes(),
        )

    def test_redis_storage(self) -> None:
        """Makes a HTTP request to in-build web server via proxy server."""
        self.__test()

    def test_memory_storage(self) -> None:
        """Makes a HTTP request to in-build web server via proxy server."""
        self.__test()
