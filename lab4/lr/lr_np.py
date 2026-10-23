from typing import List

from lr import base
import numpy as np

class LinearRegressionNumpy(base.LinearRegression):
    def fit(self, X: List[float], y: List[float]) -> base.LinearRegression:
        """Fits model to data using numpy operations."""
        X_np = np.array(X)
        y_np = np.array(y)
        X_b = np.c_[np.ones(X_np.shape[0]), X_np]  # Add bias term
        self.weights = np.linalg.inv(X_b.T @ X_b) @ X_b.T @ y_np
        self._coef = self.weights
        return self
