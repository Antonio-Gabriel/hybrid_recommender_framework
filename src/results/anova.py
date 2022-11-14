from src.results.results import AbstractResults
import statsmodels.api as sm
from statsmodels.formula.api import ols


class ANOVA(AbstractResults):
    def __init__(self, parameters: dict) -> None:
        """
        
        """

        self.axis = parameters['axis']
        self.models = parameters['models']
        # Estimate of variance, If None, will be estimated from the largest model. Default is None.
        self.scale = parameters['scale']
        # Test statistics to provide. Default is “F”. -> F, Chisp, Cp
        self.test = parameters['test']
        # The type of Anova test to perform. See notes.
        self.typ = parameters['typ']
        # Use heteroscedasticity-corrected coefficient covariance matrix. If robust covariance is desired, it is recommended to use hc3.
        # possibities = hc0,hc1, hc2, hc3, None
        self.robust = parameters['robust']

    def get_results(self):
        """

        @return: When args is a single model, return is DataFrame with columns

        """
        result = sm.stats.anova_lm(
            self.models,
            typ=self.typ
        )

        return result

    def process_parameters(self, parameters: dict) -> dict:
        """

        @param parameters: objeto com os parâmetros da classe
        @return: dicionário atualizado com esses mesmos parâmetros
        """

        pass

