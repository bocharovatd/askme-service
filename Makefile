DOCKER_COMPOSE_PATH = docker/docker-compose.yaml
SERVICE_NAME = askme-service

.PHONY: help
help:
	@echo "Available commands:"
	@echo "  docker-build      - Build containers"
	@echo "  docker-start      - Start containers"
	@echo "  docker-stop       - Stop containers"
	@echo "  docker-clean      - Stop and remove containers"
	@echo "  docker-rebuild    - Rebuild containers"
	@echo "  migrate           - Apply migrations"
	@echo "  migrate-zero      - Rollback migrations for app (usage: make migrate-zero app=<app_name>)"
	@echo "  fill-db           - Fill database (usage: make fill-db ratio=<value>)"
	@echo "  flush-db          - Flush database"
	@echo "  set-cache         - Generate cache for best members and popular tags"

.PHONY: docker-build
docker-build:
	docker compose -f $(DOCKER_COMPOSE_PATH) build

.PHONY: docker-start
docker-start:
	docker compose -f $(DOCKER_COMPOSE_PATH) up -d

.PHONY: docker-stop
docker-stop:
	docker compose -f $(DOCKER_COMPOSE_PATH) stop

.PHONY: docker-clean
docker-clean:
	docker compose -f $(DOCKER_COMPOSE_PATH) down

.PHONY: docker-rebuild
docker-rebuild: docker-clean docker-build docker-start

.PHONY: migrate
migrate:
	docker exec -it $(SERVICE_NAME) python manage.py migrate --noinput

.PHONY: migrate-zero
migrate-zero:
ifndef app
	$(error app is not set. Usage: make migrate-zero app=<app_name>)
endif
	docker exec -it $(SERVICE_NAME) python manage.py migrate $(app) zero --noinput

.PHONY: fill-db
fill-db:
ifndef ratio
	$(error ratio is not set. Usage: make fill-db ratio=<value>)
endif
	docker exec -it $(SERVICE_NAME) python manage.py fill_db $(ratio)

.PHONY: flush-db
flush-db:
	docker exec -it $(SERVICE_NAME) python manage.py flush --noinput

.PHONY: set-cache
set-cache:
	docker exec -it $(SERVICE_NAME) python manage.py generate_best_members
	docker exec -it $(SERVICE_NAME) python manage.py generate_popular_tags