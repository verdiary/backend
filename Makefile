# Makefile for a Django project located in `backend` sub-directory

# You can set these environment variables if needed
DJANGO_SETTINGS_MODULE=core.settings
PROJECT_NAME=backend

# Define your commands here
MANAGE_PY=pipenv run python $(PWD)/$(PROJECT_NAME)/manage.py

all: migrations migrate run

run:
	$(MANAGE_PY) runserver

migrations:
	$(MANAGE_PY) makemigrations

migrate:
	$(MANAGE_PY) migrate

test:
	$(MANAGE_PY) test

shell:
	$(MANAGE_PY) shell

superuser:
	$(MANAGE_PY) createsuperuser

check:
	$(MANAGE_PY) check

format:
	isort .
	black .

lint:
	flake8 .

clean:
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.log' -delete


# Docker

docker-build:
	docker build -t $(PROJECT_NAME) .

docker-run: docker-build
	docker run --rm -p 8000:8000 -e ALLOWED_HOSTS='*' --name $(PROJECT_NAME) $(PROJECT_NAME)

.PHONY: all run migrations migrate test shell superuser check format lint clean docker-build docker-run
