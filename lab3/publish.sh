#!/usr/bin/env bash
set -eu

dockerfile="${1:?Użycie: $0 </path/to/Dockerfile>}"
image="damiankwolek1/published_image"

docker build -t "$image" -f "$dockerfile" "$(dirname "$dockerfile")"
docker push "$image"
