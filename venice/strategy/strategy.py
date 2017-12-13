from abc import ABC, ABCMeta, abstractmethod


class Strategy(metaclass=ABCMeta):
    def __init__(self, api, **kwargs):
        self.api = api

    @staticmethod
    @abstractmethod
    def descr_text():
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def help_text():
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def configure_parser(parser):
        raise NotImplementedError

    @abstractmethod
    def run(self):
        raise NotImplementedError

    @abstractmethod
    def clean_up(self):
        raise NotImplementedError

    @property
    def log_file(self):
        raise NotImplementedError
