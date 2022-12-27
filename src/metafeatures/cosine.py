from src.metafeatures.metafeature import ContentBasedMetaFeature
from src.utils import process_parameters


class Cosine(ContentBasedMetaFeature):

    def __init__(self, parameters: dict) -> None:
        """
        
        """
        default_keys = set()
        parameters = process_parameters(parameters, default_keys)
        self.type = parameters['type']
        self.base_path = parameters['basePath']
        self.do_user = parameters['doUser']
        self.do_item = parameters['doItem']
        self.do_item_user = parameters['doItemUser']
        self.num_threads = parameters['numThreads']
        self.metric_parameter = parameters['metricParameter']
        self.fields = parameters['fields']
        self.items = parameters['items']

    def fit(self):
        """

        @return:
        """
        pass

    def predict(self):
        """

        @return:
        """
        pass

    def update(self, obj):
        """

        @param obj:
        @return:
        """
