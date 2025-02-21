# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

ARG PYTHON_VERSION=3.13.2
FROM python:${PYTHON_VERSION}-slim AS base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1
ENV DEBUG=False

WORKDIR /app

FROM base AS build

RUN pip install --no-cache-dir pipenv

# Install MySQL client dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends pkg-config default-libmysqlclient-dev build-essential

COPY Pipfile Pipfile.lock ./

RUN pipenv install --system --deploy

FROM base AS final

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Install MySQL client dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends default-libmysqlclient-dev

# Copy the dependencies file to the working directory.
COPY --from=build /usr/local/bin/daphne /usr/local/bin/daphne
COPY --from=build /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/

# Copy the source code into the container.
COPY scripts/docker-entrypoint.sh /docker-entrypoint.sh
COPY backend .

# Collect static files
RUN SECRET_KEY=ci BOT_TOKEN=ci python ./manage.py collectstatic --noinput

# Expose the port that the application listens on.
EXPOSE 8000

STOPSIGNAL SIGTERM

# Switch to the non-privileged user to run the application.
USER appuser

# Run the application.
ENTRYPOINT ["/docker-entrypoint.sh"]
