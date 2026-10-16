#!/usr/bin/env bash

if [ $# -ne 1 ] || [ -z "$1" ]; then
    echo "Użycie: $0 \"<komenda>\"" >&2
    exit 1
fi

target="$1"
name="${target%% *}"
found=0

for pid in $(pidof "$name"); do
    [ -O "/proc/$pid" ] || continue
    cmd=$(tr '\0' ' ' < "/proc/$pid/cmdline")
    cmd="${cmd% }"
    if [ "$cmd" = "$target" ]; then
        kill "$pid" && echo "Zakończono '$target' (PID: $pid)"
        found=1
    fi
done

if [ "$found" -eq 0 ]; then
    echo "Nie znaleziono procesu: '$target'" >&2
    exit 1
fi
