from enum import Enum


class BaseEnum(Enum):

    # def __repr__(self) -> str:
    #     if isinstance(self.value, str):
    #         return f'{self.__str__()}'
    #     return self.__str__()

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other

        if isinstance(other, Enum):
            return self.value == other.value

        return False
