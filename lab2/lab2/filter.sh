#!/usr/bin/env bash

# Litery, cyfry oraz 3 dodatkowe znaki: _ . -
ALLOWED='a-zA-Z0-9_.-'

if [ $# -eq 0 ]; then
    LC_ALL=C tr -dc "$ALLOWED" < /dev/urandom
else
    LC_ALL=C tr -dc "$ALLOWED" < /dev/urandom | head -c "$1"
    echo
fi
