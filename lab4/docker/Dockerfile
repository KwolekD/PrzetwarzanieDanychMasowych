ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim

# Dependencies pinned separately for every Python version
ARG PYTHON_VERSION
COPY requirements-${PYTHON_VERSION}.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --root-user-action=ignore -r /tmp/requirements.txt

# Project directory is mounted at /app when running container
ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    MPLCONFIGDIR=/tmp/matplotlib
WORKDIR /app
