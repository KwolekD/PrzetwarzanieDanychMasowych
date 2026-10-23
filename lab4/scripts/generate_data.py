"""Script for generation of artificial datasets."""
import argparse
from typing import List
from typing import Tuple


def get_args() -> argparse.Namespace:
    """Parses script arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--num-samples",
        required=True,
        help="Number of samples to generate",
        type=int,
    )
    parser.add_argument(
        "--out-dir",
        required=True,
        help="Name of directory to save generated data",
        type=str,
    )

    return parser.parse_args()


def generate_data(num_samples: int) -> Tuple[List[float], List[float]]:
    """Generated X, y with given number of data samples."""
    X = [float(i) for i in range(num_samples)]
    y = [float(2 * i + 1) for i in range(num_samples)]
    return X, y


def main() -> None:
    """Runs script."""
    args = get_args()
    X, y = generate_data(args.num_samples)
    print(f"Generated {len(X)} samples.")
    with open(f"{args.out_dir}/{args.num_samples}.pkl", "w") as f:
        for x, y_val in zip(X, y):
            f.write(f"{x},{y_val}\n")



if __name__ == "__main__":
    main()
