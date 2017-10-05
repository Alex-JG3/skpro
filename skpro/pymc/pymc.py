import numpy as np

from skpro.base import ProbabilisticEstimator
from .interface import InterfacePyMC

from sklearn.base import clone


class PyMC(ProbabilisticEstimator):

    class Distribution(ProbabilisticEstimator.Distribution):

        def point(self):
            return self.estimator.pymc_model.samples().mean(axis=1)

        def std(self):
            return self.estimator.pymc_model.samples().std(axis=1)

        def cdf(self, x):
            return np.array([
                self.estimator.adapter[i].cdf(x) for i in range(self.X)
            ])

        def pdf(self, x):
            return np.array([
                self.estimator.adapter[i].pdf(x) for i in range(self.X)
            ])

    def __init__(self, pymc_model=None, adapter=None):
        if not issubclass(pymc_model.__class__, InterfacePyMC):
            raise TypeError('model has to be a subclass of skpro.pymc.interface. '
                            '%s given.' % pymc_model.__class__)

        self.pymc_model = pymc_model
        self.adapter = adapter

    def fit(self, X, y):
        # fit the PyMC model
        self.pymc_model.on_fit(X, y)

        return self

    def predict(self, X):
        # predict with PyMC model
        self.pymc_model.on_predict(X)

        # initialise adapter with samples
        samples = self.pymc_model.samples()
        self.adapter = [
            clone(self.adapter)(samples[index, :]) for index in range(len(X))
        ]

        # return predicted distribution object
        return super().predict(X)
