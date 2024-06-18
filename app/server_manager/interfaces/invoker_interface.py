from abc import ABC, abstractmethod


class Invoker(ABC):
    @abstractmethod
    def register(self, package_name, command):
        pass

    @abstractmethod
    def execute(self, package_name, data):
        pass
