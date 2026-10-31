"""Script for time measurement experiments on linear regression models."""
import argparse
import gc
import json
import multiprocessing as mp
import os
import platform
import statistics
import time
from pathlib import Path
from typing import Dict
from typing import List
from typing import Tuple
from typing import Type

import numpy as np

import lr

Dataset = Tuple[List[float], List[float]]

# Fixed color and marker per model, shared by both plots
COLORS = {
    "LinearRegressionNumpy": "#2a78d6",
    "LinearRegressionProcess": "#eb6834",
    "LinearRegressionSequential": "#1baf7a",
    "LinearRegressionThreads": "#eda100",
}
MARKERS = {
    "LinearRegressionNumpy": "o",
    "LinearRegressionProcess": "s",
    "LinearRegressionSequential": "^",
    "LinearRegressionThreads": "D",
}
PARALLEL_MODELS = [lr.LinearRegressionThreads, lr.LinearRegressionProcess]
BLAS_ENV_VARS = ["OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"]


def get_args() -> argparse.Namespace:
    """Parses script arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--datasets-dir",
        required=True,
        help="Name of directory with generated datasets",
        type=str,
    )
    parser.add_argument(
        "--out-dir",
        default="data",
        help="Name of directory to save measurements and plots",
        type=str,
    )
    parser.add_argument(
        "--repeats",
        default=5,
        help="Number of time measurements for each experiment",
        type=int,
    )
    parser.add_argument(
        "--num-workers",
        default=[1, 2, 4, 8],
        nargs="+",
        help="Numbers of threads / processes checked in scaling experiment",
        type=int,
    )

    return parser.parse_args()


def load_dataset(path: Path) -> Dataset:
    """Reads dataset saved by generate_data.py (one `x,y` pair per line)."""
    X = []
    y = []
    with path.open() as file:
        for line in file:
            x_value, y_value = line.split(",")
            X.append(float(x_value))
            y.append(float(y_value))
    return X, y


def load_datasets(datasets_dir: str) -> List[Dataset]:
    """Reads all datasets from directory, sorted by number of samples."""
    datasets = [load_dataset(path) for path in Path(datasets_dir).glob("*.pkl")]
    return sorted(datasets, key=lambda dataset: len(dataset[0]))


def measure(model: lr.base.LinearRegression, dataset: Dataset, repeats: int) -> Dict:
    """Measures fit time of model on dataset `repeats` times."""
    X, y = dataset
    model.fit(X, y)  # Warm-up, not measured

    times = []
    for _ in range(repeats):
        gc.collect()
        gc.disable()
        start = time.perf_counter()
        model.fit(X, y)
        times.append(time.perf_counter() - start)
        gc.enable()

    result = {
        "model": type(model).__name__,
        "num_samples": len(X),
        "num_workers": getattr(model, "num_workers", None),
        "times": times,
        "mean": statistics.mean(times),
        "std": statistics.stdev(times) if len(times) > 1 else 0.0,
        "min": min(times),
    }
    print(
        f"{result['model']:28s} n={result['num_samples']:<10d} "
        f"workers={str(result['num_workers']):4s} "
        f"{result['mean']:.4f}s ± {result['std']:.4f}s"
    )
    return result


def run_experiments(
    models: List[Type[lr.base.LinearRegression]],
    datasets: List[Dataset],
    repeats: int = 5,
) -> List[Dict]:
    """Measures fit time of every model on every dataset."""
    results = []
    for dataset in datasets:
        for model_cls in models:
            results.append(measure(model_cls(), dataset, repeats))
    return results


def run_scaling(
    dataset: Dataset, worker_counts: List[int], repeats: int = 5
) -> List[Dict]:
    """Measures fit time of parallel models for different numbers of workers."""
    results = []
    for model_cls in PARALLEL_MODELS:
        for num_workers in worker_counts:
            results.append(measure(model_cls(num_workers=num_workers), dataset, repeats))
    return results


def get_metadata(repeats: int) -> Dict:
    """Collects environment info needed to compare results between runs."""
    return {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "start_method": mp.get_start_method(),
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
        "blas_threads": {name: os.environ.get(name) for name in BLAS_ENV_VARS},
        "repeats": repeats,
    }


def _short_name(model_name: str) -> str:
    return model_name.replace("LinearRegression", "")


def _style_axes(ax, title: str, subtitle: str) -> None:
    ax.set_title(f"{title}\n{subtitle}", loc="left", fontsize=11, color="#0b0b0b")
    ax.grid(True, color="#e4e3df", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.minorticks_off()
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color("#b5b4ad")
    ax.tick_params(colors="#52514e")
    ax.xaxis.label.set_color("#52514e")
    ax.yaxis.label.set_color("#52514e")
    ax.legend(frameon=False)


def plot_comparison(ax, comparison: List[Dict]) -> None:
    """Plots mean fit time vs dataset size for each model."""
    for model_name, color in COLORS.items():
        results = [result for result in comparison if result["model"] == model_name]
        ax.errorbar(
            [result["num_samples"] for result in results],
            [result["mean"] for result in results],
            yerr=[result["std"] for result in results],
            label=_short_name(model_name),
            color=color,
            marker=MARKERS[model_name],
            markersize=7,
            linewidth=2,
            capsize=3,
        )
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Liczba próbek")
    ax.set_ylabel("Czas fit() [s]")


def plot_scaling(ax, scaling: List[Dict], comparison: List[Dict]) -> None:
    """Plots mean fit time vs number of workers, with sequential models as reference."""
    num_samples = scaling[0]["num_samples"]
    for model_cls in PARALLEL_MODELS:
        model_name = model_cls.__name__
        results = [result for result in scaling if result["model"] == model_name]
        ax.errorbar(
            [result["num_workers"] for result in results],
            [result["mean"] for result in results],
            yerr=[result["std"] for result in results],
            label=_short_name(model_name),
            color=COLORS[model_name],
            marker=MARKERS[model_name],
            markersize=7,
            linewidth=2,
            capsize=3,
        )
    for result in comparison:
        if result["num_samples"] == num_samples and result["num_workers"] is None:
            ax.axhline(
                result["mean"],
                label=f"{_short_name(result['model'])} (referencja)",
                color=COLORS[result["model"]],
                linestyle="--",
                linewidth=1.5,
            )

    worker_counts = sorted({result["num_workers"] for result in scaling})
    ax.set_xscale("log", base=2)
    ax.set_ylim(bottom=0)
    ax.set_xticks(worker_counts)
    ax.set_xticklabels([str(count) for count in worker_counts])
    ax.set_xlabel("Liczba wątków / procesów")
    ax.set_ylabel("Czas fit() [s]")


def save_plots(
    comparison: List[Dict], scaling: List[Dict], metadata: Dict, out_dir: Path
) -> None:
    """Saves comparison and scaling plots to `out_dir`."""
    # Imported here, not at the top: with "spawn" start method (Windows) every
    # worker process re-imports this module, which would inflate process timings.
    from matplotlib.figure import Figure

    subtitle = (
        f"Python {metadata['python']}, NumPy {metadata['numpy']}, "
        f"{metadata['cpu_count']} CPU, średnia z {metadata['repeats']} pomiarów"
    )

    fig = Figure(figsize=(8, 5))
    ax = fig.subplots()
    plot_comparison(ax, comparison)
    _style_axes(ax, "Czas uczenia a rozmiar zbioru danych", subtitle)
    fig.tight_layout()
    fig.savefig(out_dir / "comparison.png", dpi=150)

    fig = Figure(figsize=(8, 5))
    ax = fig.subplots()
    plot_scaling(ax, scaling, comparison)
    title = f"Czas uczenia a liczba wątków / procesów (n={scaling[0]['num_samples']})"
    _style_axes(ax, title, subtitle)
    fig.tight_layout()
    fig.savefig(out_dir / "scaling.png", dpi=150)


def main() -> None:
    """Runs script."""
    args = get_args()

    models = [
        lr.LinearRegressionNumpy,
        lr.LinearRegressionProcess,
        lr.LinearRegressionSequential,
        lr.LinearRegressionThreads,
    ]

    datasets = load_datasets(args.datasets_dir)
    if not datasets:
        raise SystemExit(f"No datasets found in {args.datasets_dir}")

    comparison = run_experiments(models, datasets, args.repeats)
    scaling = run_scaling(datasets[-1], args.num_workers, args.repeats)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    metadata = get_metadata(args.repeats)
    with (out_dir / "time_measurements.json").open("w") as file:
        json.dump(
            {"metadata": metadata, "comparison": comparison, "scaling": scaling},
            file,
            indent=2,
        )
    save_plots(comparison, scaling, metadata, out_dir)


if __name__ == "__main__":
    main()
