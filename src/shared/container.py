from typing import TypeVar, Generic, List

T = TypeVar('T')


class Container(Generic[T]):
    """

    """
    instance_type: object

    def __init__(self, instance_type=None) -> None:
        """
        A classe Container tem o objetivo de generalizar o armazenamento de items de um tipo T

        """
        self.instance_type = instance_type
        self.__items: List[T] = []

    def push(self, item: T) -> None:
        """
        Função para inserção de um item de tipo T na lista de itens

        @param item: objeto generico de tipo T
        @return: None

        """

        if isinstance(item, self.instance_type):
            self.__items.append(item)
        else:
            raise Exception("")

    def pop(self) -> T:
        """

        @return:
        """

        return self.__items.pop()

    def insert(self, index, items: List[T]) -> None:
        """

        @param index:
        @param items:
        @return:
        """


        self.__items.insert(index, items)

    def remove(self, item: T) -> None:
        """

        @param item:
        @return:
        """
        self.__items.remove(item)

    def remove_all(self):
        """
        Remove todos os elementos da lista de itens

        @return: None
        """
        self.__items.clear()

    def print_instances(self):
        """
        Essa faz a exibição de todas as instancias da lista de items
        @return:
        """
        for i in self.__items:
            print(i)


    def is_structure_empty(self, structure: List[T]) -> bool:
        """
        Verifica se a lista de estágios de preprocessamento está vazia

        @param stages:
        @return:
        """
        if len(structure) == 0:
            return True

        return False

