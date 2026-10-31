#!/usr/bin/env bash
# Generates datasets and runs linear regression experiments under several
# Python versions (Docker) and numbers of BLAS threads.
set -euo pipefail

cd "$(dirname "$0")"

PYTHON_VERSIONS=(3.10 3.12 3.14)
NUM_SAMPLES=(100 1000 10000 100000 1000000)
BLAS_THREADS=(1 4)
NUM_WORKERS=(1 2 4 8)
REPEATS=5

IMAGE=lab4-lr
DATASETS_DIR=datasets
RESULTS_DIR=data

# Git Bash on Windows: disable path conversion and mount Windows path
export MSYS_NO_PATHCONV=1
HOST_DIR="$(pwd -W 2>/dev/null || pwd)"

# Usage: docker_run <python-version> <blas-threads> <command...>
docker_run() {
    local version=$1
    local blas_threads=$2
    shift 2
    docker run --rm \
        --user "$(id -u):$(id -g)" \
        -v "${HOST_DIR}:/app" \
        -e OMP_NUM_THREADS="${blas_threads}" \
        -e OPENBLAS_NUM_THREADS="${blas_threads}" \
        -e MKL_NUM_THREADS="${blas_threads}" \
        "${IMAGE}:py${version}" "$@"
}

echo "=== Building images"
for version in "${PYTHON_VERSIONS[@]}"
do
    docker build -q \
        --build-arg PYTHON_VERSION="${version}" \
        -t "${IMAGE}:py${version}" \
        docker/
done

echo "=== Generating datasets"
for num_samples in "${NUM_SAMPLES[@]}"
do
    docker_run "${PYTHON_VERSIONS[0]}" 1 \
        python scripts/generate_data.py \
            --num-samples "${num_samples}" \
            --out-dir "${DATASETS_DIR}"
done

for version in "${PYTHON_VERSIONS[@]}"
do
    for blas_threads in "${BLAS_THREADS[@]}"
    do
        echo "=== Python ${version}, BLAS threads: ${blas_threads}"
        docker_run "${version}" "${blas_threads}" \
            python scripts/run_experiments.py \
                --datasets-dir "${DATASETS_DIR}" \
                --out-dir "${RESULTS_DIR}/py${version}-blas${blas_threads}" \
                --repeats "${REPEATS}" \
                --num-workers "${NUM_WORKERS[@]}"
    done
done

echo "=== Comparing Python versions and BLAS threads"
docker_run "${PYTHON_VERSIONS[-1]}" 1 \
    python scripts/compare_versions.py --results-dir "${RESULTS_DIR}"
