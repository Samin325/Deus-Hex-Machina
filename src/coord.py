# coord.py

class Coord:
    def __init__(self, x: int, y: int) -> None:
        # may need to revise parameters later
        self.__x = x
        self.__y = y
        self.__name = Coord.cart2str(x, y)

    def __str__(self) -> str:
        return self.__name

    def getx(self) -> int:
        return self.__x
    
    def gety(self) -> int:
        return self.__y

    def __hash__(self) -> int:
        return self.__x * 32 + self.__y  # doesn't really matter tbh

    def __eq__(self, __o: object) -> bool:
        return self.__x == __o.getx() and self.__y == __o.gety()

    @staticmethod
    def cart2str(x: int, y: int) -> str:
        # TODO: finish
        return "a1"

    @staticmethod
    def str2cart(name: str) -> tuple:
        # TODO: finish
        # may not need this one at all
        return (1, 1)
