from typing import List

from lr import base


class LinearRegressionSequential(base.LinearRegression):
    def fit(self, X: List[float], y: List[float]) -> base.LinearRegression:
        """Fits model to data using least squares sums computed sequentially."""
        self._coef = base.coef_from_sums(base.partial_sums(X, y))
        return self

    def predict(self, X: List[float]) -> List[float]:
        """Predicts target values for given input data (pure Python)."""
        if self._coef is None:
            raise RuntimeError("Please fit model before prediction")

        intercept, slope = self._coef
        return [intercept + slope * x_value for x_value in X]
