from typing import List

from lr import base


class LinearRegressionSequential(base.LinearRegression):
    def __init__(self, learning_rate: float = 0.01, num_epochs: int = 1000) -> None:
        """Initializes model with given hyperparameters."""
        self.learning_rate = learning_rate
        self.num_epochs = num_epochs

    def fit(self, X: List[float], y: List[float]) -> base.LinearRegression:
        """Fits model to data using sequential gradient descent."""
        self._initialize_weights()
        for _ in range(self.num_epochs):
            for x_i, y_i in zip(X, y):
                y_pred = self.predict([x_i])[0]
                error = y_pred - y_i
                self.weights[0] -= self.learning_rate * error
                self.weights[1] -= self.learning_rate * error * x_i
        return self

    def predict(self, X: List[float]) -> List[float]:
        """Predicts target values for given input data."""
        return [self.weights[0] + self.weights[1] * x_i for x_i in X]

    def _initialize_weights(self) -> None:
        """Initializes model weights to zero."""
        self.weights = [0.0, 0.0]
        self._coef = self.weights