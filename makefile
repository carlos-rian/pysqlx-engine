tests-databases:
	docker-compose \
	--file tests/docker/docker-compose.yml up \
	--build \
	--detach 

tests-coverage:
	make tests-databases && \
	poetry run pytest tests -v -x \
		--doctest-modules \
		--ignore=tests/ \
		--cov=sqlx_engine \
		--durations=0 \
		--cov-report=html:tests/results/html \
		--junitxml=tests/results/xml/test-results.xml

requirements:
	poetry export -f requirements.txt --output requirements.txt  --without-hashes

requirements-dev:
	poetry export --dev -f requirements.txt --output requirements-dev.txt  --without-hashes


req:
	make requirements && \
	make requirements-dev