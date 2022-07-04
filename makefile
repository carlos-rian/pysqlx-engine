databases-tests:
	docker-compose \
	--file tests/docker/docker-compose.yml up \
	--force-recreate \
	--build 