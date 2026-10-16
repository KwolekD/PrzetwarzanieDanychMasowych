#!/usr/bin/env bash

if [ $# -lt 3 ]; then
    echo "Użycie: $0 <user1@host1:/ścieżka/> <user2@host2:/ścieżka/> <plik>[:<nowa-nazwa>] ..." >&2
    exit 1
fi

src="${1%/}"
dst="${2%/}"
shift 2
failed=0

for spec in "$@"; do
    file="${spec%%:*}"
    new="${spec#*:}"
    [ -z "$new" ] && new="$file"

    if [ -z "$file" ]; then
        echo "Błąd: brak nazwy pliku w '$spec'" >&2
        failed=$((failed + 1))
        continue
    fi

    # -3: przesył idzie przez lokalną maszynę, hosty nie muszą mieć dostępu do siebie nawzajem
    if scp -3 "$src/$file" "$dst/$new"; then
        echo "Skopiowano: $file -> $new"
    else
        echo "Błąd: nie udało się skopiować '$file'" >&2
        failed=$((failed + 1))
    fi
done

[ "$failed" -eq 0 ] || exit 1