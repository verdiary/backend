#!/bin/sh

set -e

PORT=${PORT:-8000}
HOST=${HOST:-0.0.0.0}

python manage.py migrate
exec daphne -b ${HOST} -p ${PORT} core.asgi:application
