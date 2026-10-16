#!/usr/bin/env bash

if [ $# -lt 1 ]; then
    echo "Użycie: $0 \"<komenda>\"" >&2
    exit 1
fi

bash -c "$1" &
echo "Uruchomiono w tle: '$1' (PID: $!)"