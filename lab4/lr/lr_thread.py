from typing import List

from lr import base
import threading as th

class LinearRegressionThreads(base.LinearRegression):
    def fit(self, X: List[float], y: List[float]) -> base.LinearRegression:
        """Fits model to data using threads."""
        self._initialize_weights()
        self.batch_size = 16  # Each thread processes one sample

        for _ in range(self.num_epochs):
            threads = []
            for i in range(0, len(X), self.batch_size):
                X_batch = X[i:i + self.batch_size]
                y_batch = y[i:i + self.batch_size]
                thread = th.Thread(target=self._update_weights, args=(X_batch, y_batch))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()
