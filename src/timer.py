# timer.py

from time import perf_counter


class Timer:
    def __init__(self) -> None:
        self.__start_time = perf_counter()

    def reset(self) -> None:
        self.__start_time = perf_counter()

    def get_time(self) -> float:
        return perf_counter() - self.__start_time
