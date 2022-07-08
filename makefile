databases-tests:
	docker-compose \
	--file tests/docker/docker-compose.yml up \
	--force-recreate \
	--build 

test-coverage:
	poetry run pytest tests -v -x \
		--doctest-modules \
		--ignore=tests/ \
		--cov=sqlx_engine \
		--cov-config=tests/results/ \
		--cov-report=html:tests/results/html \
		--junitxml=tests/results/xml/test-results.xml