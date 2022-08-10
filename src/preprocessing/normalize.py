from src.preprocessing.preprocessing import AbstractPreProcessing
from sklearn.preprocessing import normalize


class NormalizeProcessing(AbstractPreProcessing):

    def __init__(self):
        """

        """
        super().__init__()

    def pre_processing(self, data):
        return normalize(data)
