# coord.py


class Coord:
    def __init__(self, x: int, y: int) -> None:
        """ Create a Coord object

        Parameters:
            x: (int) position across (left to right). converted to letter
            y: (int) position upwards. remains as number
        """
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
        return self.__x * 32 + self.__y

    def __eq__(self, __o: object) -> bool:
        return self.__x == __o.getx() and self.__y == __o.gety()

    @staticmethod
    def cart2str(x: int, y: int) -> str:
        """ Convert a cartesian pair to a chess-style string

        Parameters:
            x: (int) position across. converted to letter
            y: (int) position downwards. remains as number

        Returns: (str)
            chess-style coordinate eg. "b5"
        """
        if x <= 0:
            letter = '-'
        elif x > 26:
            letter = '+'
        else:
            letter = chr(ord('a') + x - 1)
        if y < 0:
            y = 0
        return letter + str(y)

    @staticmethod
    def str2cart(name: str) -> tuple:
        """ Convert a chess-style string to a cartesian pair

        Parameters:
            name: (str) chess-style string eg. "b5"

        Returns: (tuple[int, int])
            equivalent x and y coordinates
        """
        x = ord(name[0]) - ord('a') + 1
        y = int(name[1:])
        return (x, y)
