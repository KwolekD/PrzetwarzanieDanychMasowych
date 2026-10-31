from concurrent.futures import ProcessPoolExecutor
from typing import List

from lr import base


class LinearRegressionProcess(base.LinearRegression):
    def __init__(self, num_workers: int = 4) -> None:
        super().__init__()
        self.num_workers = num_workers

    def fit(self, X: List[float], y: List[float]) -> base.LinearRegression:
        """Fits model to data computing partial sums of batches in processes."""
        X_batches = base.split_batches(X, self.num_workers)
        y_batches = base.split_batches(y, self.num_workers)

        with ProcessPoolExecutor(max_workers=len(X_batches)) as executor:
            partials = list(executor.map(base.partial_sums, X_batches, y_batches))

        self._coef = base.coef_from_sums(base.aggregate_sums(partials))
        return self
