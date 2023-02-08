tests-databases:
	docker-compose \
	--file tests/docker/docker-compose.yml up \
	--build \
	--detach 

upt-deps:
	poetry add \
		pydantic@latest \
		pysqlx-core@latest \
		typing-extensions@latest \
		Pygments@latest

upt-dev-deps:
	poetry add --dev \
		isort \
		black@latest \
		pytest@latest \
		pytest-asyncio@latest \
		pytest-cov@latest \
		pytest-dotenv@latest \
		pytest-xdist@latest \
		toml@latest \
		httpx@latest 


#--ignore=tests/benchmark 
tests-coverage:
	make tests-databases && \
	poetry run pytest tests -v -x \
		--doctest-modules \
		--ignore=tests/benchmark \
		--cov=pysqlx_engine \
		--cov=tests \
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

server-docs:
	mkdocs serve