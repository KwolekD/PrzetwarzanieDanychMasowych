from typing import List

from lr import base
import numpy as np

class LinearRegressionNumpy(base.LinearRegression):
    def fit(self, X: List[float], y: List[float]) -> base.LinearRegression:
        """Fits model to data using numpy operations."""
        X_np = np.asarray(X, dtype=np.float64)
        y_np = np.asarray(y, dtype=np.float64)
        design_matrix = np.column_stack([np.ones(len(X_np)), X_np])  # Add bias term
        self._coef = np.linalg.lstsq(design_matrix, y_np, rcond=None)[0]
        return self
