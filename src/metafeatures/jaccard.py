from src.metafeatures.metafeature import ContentBasedMetaFeature
from src.utils import process_parameters


class Jaccard(ContentBasedMetaFeature):
    def __init__(self, parameters: dict) -> None:
        super().__init__(parameters)
        default_keys = {
            'type',
            'basePath',
            'doUser',
            'doItem',
            'doItemUser',
            'metricParameter',
        }
        parameters = process_parameters(parameters, default_keys)
        self.type = parameters.get('type')
        self.base_path = parameters.get('basePath')
        self.do_user = parameters.get('doUser')
        self.do_item = parameters.get('doItem')
        self.do_item_user = parameters.get('doItemUser')
        self.num_threads = parameters.get('numThreads')
        self.metric_parameter = parameters.get('metricParameter')
        self.fields = parameters.get('fields')

    #        self.items = parameters['items']

    def update(self, obj):
        """

        @param obj:
        @return:
        """
        pass


