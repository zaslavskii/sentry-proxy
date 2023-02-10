.PHONY: help tests lint pyfmt clean

tests:
	python -m pytest tests --cov=sentry_proxy

unit_tests:
	python -m pytest tests -m "not integration" --cov=sentry_proxy

integration_tests:
	python -m pytest tests -m "integration" --cov=sentry_proxy

docker_tests:
	docker-compose -f docker-compose.yml -f docker-compose.tests.yml run --build --rm proxy make lint tests

lint:
	python -m mypy sentry_proxy
	python -m isort . --diff --check-only
	python -m black --check .

fmt:
	python -m isort .
	python -m black .

clean:
	rm -rf .venv
	find . -name \*.pyc -delete
	find . -name .coverage* -delete
