import abc

class Strategy(metaclass=abc.ABCMeta):
    def __init__(self, api, **kwargs):
        self._api = api

    @staticmethod
    @abc.abstractmethod
    def help_text():
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def configure_parser(parser):
        raise NotImplementedError

    @abc.abstractmethod
    def run():
        raise NotImplementedError
