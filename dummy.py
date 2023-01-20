from sentry_sdk import init

SENTRY_DSN = ""
SENTRY_PROXY = "http://127.0.0.1:8899"
SENTRY_PROXY_CA_CERT = "./certs/ca-cert.pem"


init(
    SENTRY_DSN,
    http_proxy=SENTRY_PROXY,
    environment="dev.chainstack.com",
    ca_certs=SENTRY_PROXY_CA_CERT,
)
if __name__ == '__main__':
    division_by_zero = 1 / 0
