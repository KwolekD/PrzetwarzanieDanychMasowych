from __future__ import annotations

import abc
import math
from typing import List
from typing import Tuple

import numpy as np

# (count, sum of x, sum of y, sum of x^2, sum of x*y)
Sums = Tuple[int, float, float, float, float]


class ScikitPredictor(abc.ABC):
    @abc.abstractmethod
    def fit(self, X, y):
        pass

    @abc.abstractmethod
    def predict(self, X):
        pass


class LinearRegression(ScikitPredictor):
    def __init__(self):
        self._coef = None

    @abc.abstractmethod
    def fit(self, X: List[float], y: List[float]) -> LinearRegression:
        pass

    def predict(self, X: List[float]) -> np.ndarray:
        if self._coef is None:
            raise RuntimeError("Please fit model before prediction")

        return self._coef[0] + self._coef[1] * np.array(X)


def partial_sums(X: List[float], y: List[float]) -> Sums:
    """Computes sums needed by least squares method (pure Python)."""
    sum_x = 0.0
    sum_y = 0.0
    sum_xx = 0.0
    sum_xy = 0.0
    for x_value, y_value in zip(X, y):
        sum_x += x_value
        sum_y += y_value
        sum_xx += x_value * x_value
        sum_xy += x_value * y_value
    return len(X), sum_x, sum_y, sum_xx, sum_xy


def aggregate_sums(partials: List[Sums]) -> Sums:
    """Adds partial sums computed on separate batches."""
    return tuple(sum(column) for column in zip(*partials))


def coef_from_sums(sums: Sums) -> List[float]:
    """Computes [intercept, slope] from least squares sums."""
    count, sum_x, sum_y, sum_xx, sum_xy = sums
    slope = (count * sum_xy - sum_x * sum_y) / (count * sum_xx - sum_x * sum_x)
    intercept = (sum_y - slope * sum_x) / count
    return [intercept, slope]


def split_batches(values: List[float], num_batches: int) -> List[List[float]]:
    """Splits list into at most `num_batches` contiguous batches."""
    batch_size = math.ceil(len(values) / num_batches)
    return [
        values[start:start + batch_size]
        for start in range(0, len(values), batch_size)
    ]
