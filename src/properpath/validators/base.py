from abc import ABC, abstractmethod


class ValidationError(Exception): ...


class Validator(ABC):
    """
    The abstract base class for validators.
    """

    @abstractmethod
    def validate(self, *args, **kwargs): ...
