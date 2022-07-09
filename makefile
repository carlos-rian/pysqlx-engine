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
		--cov-report=html:tests/results/html \
		--junitxml=tests/results/xml/test-results.xml