#!/bin/sh

set -e

PORT=${PORT:-8000}
HOST=${HOST:-0.0.0.0}
BOT_MODE=${BOT_MODE:-webhook}

python manage.py migrate
python manage.py syncbot

case "$BOT_MODE" in
  webhook)
    exec daphne -b "${HOST}" -p "${PORT}" core.asgi:application
    ;;
  polling)
    exec python manage.py runbot
    ;;
  *)
    echo "Unsupported BOT_MODE: ${BOT_MODE}. Use 'webhook' or 'polling'." >&2
    exit 1
    ;;
esac
