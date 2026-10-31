"""Script for generation of artificial datasets."""
import argparse
import os
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
    """Generates X, y with given number of data samples."""
    X = [float(index) for index in range(num_samples)]
    y = [float(2 * index + 1) for index in range(num_samples)]
    return X, y


def main() -> None:
    """Runs script."""
    args = get_args()
    if args.num_samples <= 0:
        raise ValueError("Number of samples must be a positive integer.")
    if not args.out_dir:
        raise ValueError("Output directory must be specified.")
    if not os.path.exists(args.out_dir):
        os.makedirs(args.out_dir)
    X, y = generate_data(args.num_samples)
    print(f"Generated {len(X)} samples.")
    with open(f"{args.out_dir}/{args.num_samples}.pkl", "w") as file:
        for x_value, y_value in zip(X, y):
            file.write(f"{x_value},{y_value}\n")



if __name__ == "__main__":
    main()
