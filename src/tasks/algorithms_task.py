from lenskit.algorithms.basic import UnratedItemCandidateSelector
import numpy as np
from src.experiments.experiment_handler import ExperimentHandler
from joblib import dump, load
from lenskit.algorithms.ranking import TopN
from src.tasks.task import Task
from src.data.loader import Loader
from src.utils import hrf_experiment_output_path
import pandas as pd
from lenskit.batch import predict, recommend
from lenskit.algorithms import Recommender
from src.recommenders.recommenders_container import RecommendersContainer
import os
import traceback


class AlgorithmsTask(Task):
    def __init__(self, algorithm: RecommendersContainer, args=None):
        self.algorithm_instances: RecommendersContainer = algorithm
        self.number_of_recommendations = self.algorithm_instances.number_of_recommendations
        self.experiment_output_dir = hrf_experiment_output_path()
        self.preprocessing_output_dir = self.experiment_output_dir.joinpath("preprocessing/")
        self.algorithms_output_dir = self.experiment_output_dir.joinpath("models/results/")
        self.predictions_output_dir = self.algorithms_output_dir.joinpath("predictions/")
        self.rankings_output_dir = self.algorithms_output_dir.joinpath("rankings/")
        self.recommendations_output_dir = self.algorithms_output_dir.joinpath("recommendations/")

    def check_args(self, args):
        """

        @param args:
        @return:
        """
        pass

    def get_fold_file_names(self, fold_type: str) -> list:
        if fold_type not in ['train', 'validation']:
            raise Exception("O valor de fold_type está invalido, tente: train ou validation")

        folds_directory = self.preprocessing_output_dir.joinpath("folds/{}/".format(fold_type))
        file_names = []
        for path in os.scandir(folds_directory):
            if path.is_file():
                file_names.append(path.name)

        return file_names

    def get_default_files_to_train_and_test(self):
        default_splitted_files = {
            "xtrain": self.preprocessing_output_dir.joinpath('xtrain.csv'),
            "xtest": self.preprocessing_output_dir.joinpath('xtest.csv'),
            "ytest": self.preprocessing_output_dir.joinpath('ytest.csv'),
            "ytrain": self.preprocessing_output_dir.joinpath('ytrain.csv')
        }
        return default_splitted_files

    def predict_to_users(self, algorithm, users, items, rating: pd.Series = None):  # tá errado
        predictions_df = pd.DataFrame(columns=['user', 'item', 'prediction'])
        number_of_items_rankeds = 10
        for u in users:
            prediction_result = algorithm.predict_for_user(u, items, rating)
            print("prediction result: ", prediction_result)
            user_id = [u] * number_of_items_rankeds
            algorithm_name = [algorithm.__class__.__name__] * number_of_items_rankeds
            prediction_result['user'] = pd.Series(user_id)
            prediction_result['algorithm'] = pd.Series(algorithm_name)
            predictions_df = pd.concat([predictions_df, prediction_result], ignore_index=True)

        return predictions_df

    def check_if_folds_is_empty(self) -> bool:
        """
        Função para verificar se os folds existem, com o objetivo de decidir se eles serõo usados
        ou se a aplicação vai utilizar os dados a partir de sua divisão normal.

        @return: bool
        """

        folds_path = self.preprocessing_output_dir.joinpath(
            "folds/train/"
        )

        folds_dir = os.listdir(folds_path)
        if len(folds_dir) == 0:
            return False

        return True

    def fold_execution(self):
        train_fold_files = self.get_fold_file_names('train')
        validation_fold_files = self.get_fold_file_names('validation')
        fold_files = zip(train_fold_files, validation_fold_files)

        if len(train_fold_files) == 0:
            raise Exception("Os arquivos de fold de treino não foram encontrados")

        test_dataset_path = self.experiment_output_dir.joinpath("preprocessing/xtest.csv")
        test_dataset = pd.read_csv(test_dataset_path)

        content_based_df_path = self.experiment_output_dir.joinpath("preprocessing/content-based-dataset.csv")
        content_based_df = pd.read_csv(content_based_df_path)

        for train_file, validation_file in fold_files:
            train_dataset_path = self.preprocessing_output_dir.joinpath("folds/train/").joinpath(train_file)
            validation_dataset_path = self.preprocessing_output_dir.joinpath("folds/validation").joinpath(
                validation_file)

            train_dataset = pd.read_csv(train_dataset_path, index_col=[0])
            validation_dataset = pd.read_csv(validation_dataset_path, index_col=[0])

            fold_name = train_file.split(".")
            fold_name = fold_name[0]

            algorithms = self.handle_algorithms_tasks(
                self.algorithm_instances,
                train_dataset,
                fold_name,
                validation_dataset,
                content_based_df
            )

        return True

    def default_execution(self):
        files_path = self.get_default_files_to_train_and_test()
        try:
            xtrain = pd.read_csv(files_path.get('xtrain'))
            ytrain = pd.read_csv(files_path.get('ytrain'))
            ytest = pd.read_csv(files_path.get('ytest'))
            xtest = pd.read_csv(files_path.get('xtest'))

            algorithms = self.handle_algorithms_task_default(
                algorithms=self.algorithm_instances,
                xtrain=xtrain,
                xtest=xtest,
                ytrain=ytrain,
                ytest=ytest,
                train_dataset_name='xtrain'
            )

            return algorithms
        except Exception as e:
            print(e)

    def run(self):
        try:
            is_folds_directory_exists = self.check_if_folds_is_empty()
            if is_folds_directory_exists is True:
                result = self.fold_execution()
                return result
            else:
                result = self.default_execution()
                return result

        except Exception as e:
            print(e)
            print(traceback.print_exc())

    def topn_process(self, algorithm, ratings: pd.DataFrame):
        try:
            if algorithm.__class__.__name__ == "RandomItem":  # Verificar se posso evitar isso
                return None

            users = np.unique(ratings['user'].values)
            items = ratings['item'].values

            select = UnratedItemCandidateSelector()

            topn_dataframe = pd.DataFrame(columns=['user', 'item', 'score'])

            top_n = TopN(algorithm, select)
            number_of_items_rankeds = self.number_of_recommendations
            for u in users:
                recs = top_n.recommend(
                    u,
                    number_of_items_rankeds,
                    items
                )

                user_id = [u] * number_of_items_rankeds
                algorithm_name = [algorithm.__class__.__name__] * number_of_items_rankeds
                recs['user'] = pd.Series(user_id)
                recs['algorithm'] = pd.Series(algorithm_name)
                topn_dataframe = pd.concat([topn_dataframe, recs], ignore_index=True)

            return topn_dataframe

        except Exception as err:
            print(err)
            print(traceback.print_exc())
            return None

    def _recommend_to_content_based(self, algorithm, algorithm_name, dataset, dataset_name):
        algorithm.fit(dataset)
        recs = algorithm.recommend(None, 0, dataset)
        if recs is not None:
            recommendation_file_name = algorithm_name + "-" + dataset_name + "-" + "recommendations-content-based.csv"
            recs.to_csv(self.recommendations_output_dir.joinpath(recommendation_file_name), index=False)

    def handle_algorithms_task_default(self,
                                       algorithms: RecommendersContainer,
                                       xtrain: pd.DataFrame = pd.DataFrame(),
                                       xtest: pd.DataFrame = pd.DataFrame(),
                                       ytrain: pd.Series = None,
                                       ytest: pd.Series = None,
                                       content_based_dataset: pd.DataFrame = pd.DataFrame(),
                                       train_dataset_name: str = ""
                                       ):

        try:
            for algorithm in algorithms.items[0]:
                algorithm_name = algorithm.__class__.__name__
                print("Algorithm name: ", algorithm_name)
                print("dataset_name:", train_dataset_name)

                if algorithm_name == "ContentBasedRecommender":
                    self._recommend_to_content_based(
                        algorithm, algorithm_name, content_based_dataset, "movies"
                    )
                    continue

                algorithm.fit(xtrain)

                path = hrf_experiment_output_path().joinpath("models/trained_models/")
                path = path.joinpath(algorithm_name + "-" + train_dataset_name + ".joblib")
                dump(algorithm, path)

                topn_result = self.topn_process(algorithm, xtrain)
                ranking_file_name = algorithm_name + "-" + train_dataset_name + "-" + "ranking.csv"
                if topn_result is not None:
                    topn_result.to_csv(self.rankings_output_dir.joinpath(ranking_file_name), index=False)

                dataset_copy = xtrain.copy()
                dataset_copy.drop(columns=['rating'], inplace=True)

                preds = predict(algorithm, xtrain)

                if preds is not None:
                    prediction_file_name = algorithm_name + "-" + train_dataset_name + "-" + "predictions.csv"
                    preds.to_csv(self.predictions_output_dir.joinpath(prediction_file_name), index=False)

                users = np.unique(xtest['user'].values)

                recs = algorithm.recommend(users, self.number_of_recommendations)
                if recs is not None:
                    recommendation_file_name = algorithm_name + "-" + train_dataset_name + "-" + "recommendations.csv"
                    recs.to_csv(self.recommendations_output_dir.joinpath(recommendation_file_name), index=False)

            return True

        except Exception as err:
            print("Error: ", err)
            print(traceback.print_exc())
            return None

    def handle_algorithms_tasks(self,
                                algorithms: RecommendersContainer,
                                dataset: pd.DataFrame,
                                dataset_name: str,
                                test_dataset: pd.DataFrame,
                                content_based_dataset: pd.DataFrame):

        try:
            for algorithm in algorithms.items[0]:
                algorithm_name = algorithm.__class__.__name__
                print("Algorithm name: ", algorithm_name)
                print("dataset_name:", dataset_name)
                print("Number of recomendations: ", algorithm.number_of_recommendations)
                if algorithm_name == "ContentBasedRecommender":
                    self._recommend_to_content_based(
                        algorithm, algorithm_name, content_based_dataset, "movies"
                    )
                    continue

                algorithm.fit(dataset)

                path = hrf_experiment_output_path().joinpath("models/trained_models/")
                path = path.joinpath(algorithm_name + "-" + dataset_name + ".joblib")
                dump(algorithm.fittable, path)

                topn_result = self.topn_process(algorithm, dataset)
                ranking_file_name = algorithm_name + "-" + dataset_name + "-" + "ranking.csv"
                if topn_result is not None:
                    topn_result.to_csv(self.rankings_output_dir.joinpath(ranking_file_name), index=False)

                dataset_copy = dataset.copy()
                dataset_copy.drop(columns=['rating'], inplace=True)

                preds = predict(algorithm, dataset)

                if preds is not None:
                    prediction_file_name = algorithm_name + "-" + dataset_name + "-" + "predictions.csv"
                    preds.to_csv(self.predictions_output_dir.joinpath(prediction_file_name), index=False)

                users = np.unique(test_dataset['user'].values)

                # Tenho que padronizar quantas recomendações serão feitas
                recs = algorithm.recommend(users, self.number_of_recommendations)
                if recs is not None:
                    recommendation_file_name = algorithm_name + "-" + dataset_name + "-" + "recommendations.csv"
                    recs.to_csv(self.recommendations_output_dir.joinpath(recommendation_file_name), index=False)

            return True

        except Exception as err:
            print("Error: ", err)
            print(traceback.print_exc())
            return None


def run_algorithms_task():
    print(" => Inicio da tarefa dos algoritmos")
    loader = Loader()
    config_obj = loader.load_json_file("config.json")

    experiments = config_obj['experiments']
    exp_handler = ExperimentHandler(
        experiments=experiments
    )
    experiment = exp_handler.get_experiment("exp1")
    experiment_instances = experiment.instances

    algorithms = experiment_instances['recommenders']
    algorithms_task = AlgorithmsTask(algorithms)
    algorithms_task.run()

    print(" => Finalizando a tarefa dos algoritmos")


if __name__ == "__main__":
    run_algorithms_task()
