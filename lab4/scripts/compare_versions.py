"""Script comparing time measurements between Python versions and BLAS threads."""
import argparse
import json
from pathlib import Path
from typing import Dict
from typing import List

import numpy as np
from matplotlib.figure import Figure

MODELS = [
    "LinearRegressionNumpy",
    "LinearRegressionProcess",
    "LinearRegressionSequential",
    "LinearRegressionThreads",
]
BLAS_COLORS = ["#2a78d6", "#eb6834", "#1baf7a"]


def get_args() -> argparse.Namespace:
    """Parses script arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--results-dir",
        required=True,
        help="Name of directory with results of run_experiments.py (one subdirectory per run)",
        type=str,
    )

    return parser.parse_args()


def load_runs(results_dir: Path) -> List[Dict]:
    """Reads measurements of every run saved in subdirectories of `results_dir`."""
    runs = []
    for path in sorted(results_dir.glob("*/time_measurements.json")):
        with path.open() as file:
            runs.append(json.load(file))
    return runs


def _blas_threads(run: Dict) -> str:
    return run["metadata"]["blas_threads"]["OPENBLAS_NUM_THREADS"]


def _short_name(model_name: str) -> str:
    return model_name.replace("LinearRegression", "")


def mean_times(runs: List[Dict], num_samples: int) -> Dict:
    """Maps (Python version, BLAS threads, model) to mean fit time [ms]."""
    times = {}
    for run in runs:
        for result in run["comparison"]:
            if result["num_samples"] == num_samples:
                key = (run["metadata"]["python"], _blas_threads(run), result["model"])
                times[key] = result["mean"] * 1000
    return times


def summary_table(runs: List[Dict], times: Dict) -> str:
    """Builds markdown table with mean fit times [ms] of every run."""
    header = ["Python", "NumPy", "BLAS", "start method"]
    header += [f"{_short_name(model)} [ms]" for model in MODELS]
    lines = ["| " + " | ".join(header) + " |", "|" + " --- |" * len(header)]
    for run in runs:
        metadata = run["metadata"]
        blas_threads = _blas_threads(run)
        cells = [metadata["python"], metadata["numpy"], blas_threads, metadata["start_method"]]
        cells += [f"{times[(metadata['python'], blas_threads, model)]:.2f}" for model in MODELS]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def plot_versions(runs: List[Dict], times: Dict, num_samples: int, path: Path) -> None:
    """Plots mean fit time per Python version and BLAS threads, one panel per model."""
    python_versions = sorted({run["metadata"]["python"] for run in runs})
    blas_values = sorted({_blas_threads(run) for run in runs})
    numpy_versions = {run["metadata"]["python"]: run["metadata"]["numpy"] for run in runs}
    positions = np.arange(len(python_versions))
    bar_width = 0.8 / len(blas_values)

    fig = Figure(figsize=(10, 7))
    axes = fig.subplots(2, 2).flatten()
    for ax, model in zip(axes, MODELS):
        for index, blas_threads in enumerate(blas_values):
            offset = (index - (len(blas_values) - 1) / 2) * bar_width
            heights = [times[(version, blas_threads, model)] for version in python_versions]
            ax.bar(
                positions + offset,
                heights,
                bar_width * 0.9,
                color=BLAS_COLORS[index],
                label=f"wątki BLAS: {blas_threads}",
            )
        ax.set_title(_short_name(model), loc="left", fontsize=11, color="#0b0b0b")
        ax.set_xticks(positions)
        ax.set_xticklabels(
            [f"Python {version}\nNumPy {numpy_versions[version]}" for version in python_versions],
            fontsize=8,
        )
        ax.set_ylabel("Czas fit() [ms]", color="#52514e")
        ax.grid(True, axis="y", color="#e4e3df", linewidth=0.8)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color("#b5b4ad")
        ax.tick_params(colors="#52514e")

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper right", ncol=len(blas_values), frameon=False)
    fig.suptitle(
        f"Czas uczenia wg wersji Pythona i liczby wątków BLAS (n={num_samples})",
        x=0.01,
        ha="left",
        fontsize=12,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(path, dpi=150)


def main() -> None:
    """Runs script."""
    args = get_args()
    results_dir = Path(args.results_dir)

    runs = load_runs(results_dir)
    if not runs:
        raise SystemExit(f"No measurements found in {results_dir}")
    num_samples = max(result["num_samples"] for result in runs[0]["comparison"])
    times = mean_times(runs, num_samples)

    table = summary_table(runs, times)
    print(table)
    summary = f"Średni czas fit() dla n={num_samples}\n\n{table}\n"
    (results_dir / "summary.md").write_text(summary, encoding="utf-8")
    plot_versions(runs, times, num_samples, results_dir / "versions.png")


if __name__ == "__main__":
    main()
