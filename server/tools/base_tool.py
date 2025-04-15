from abc import ABC, abstractmethod


class BaseTool(ABC):
    """
    Abstract class for Doubt Clearance Tools
    """

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def run(self, **kwargs):
        """
        The main execution method for all tools

        Args:
            **kwargs: Arbitrary keyword arguments needed by the specific tool.

        Returns:
            generated_response, link, type

        Raises:
            ValueError: If required arguments are missing or invalid.
            NotImplementedError: If the subclass doesn't implement this method.
            Exception: For any other tool-specific errors during execution.
        """
        pass

    def __str__(self):
        return self.__class__.__name__
