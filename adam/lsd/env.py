from __future__ import annotations

from collections import UserDict


class Env(UserDict[str, tuple]):
    """
    A class that represents an environment in which variables are bound to values.

    This class is a specialized dictionary where:
    - The keys are variable names (strings).
    - The values are tuples, even if they represent a single value.
    - An empty tuple is used to represent "None", indicating that no value is bound to the variable.

    Attributes:
        data (dict): A dictionary that holds variable bindings.
    """

    def __init__(self, bindings={}, **kwargs):
        """
        Initializes an `Env` object with a set of variable bindings.

        Args:
            bindings (dict, optional): A dictionary of initial variable bindings. Defaults to an empty dictionary.
            **kwargs: Additional keyword arguments to add to the environment.

        Example:
            env = Env({"x": (1,)})  # Creates an environment where 'x' is bound to (1,).
        """
        super().__init__({**bindings, **kwargs})

    def bind(self, name: str, value):
        """
        Binds a variable to a value in the environment.

        This method updates the environment by adding or updating a variable binding.

        Args:
            name (str): The name of the variable to bind.
            value (any): The value to bind to the variable.

        Returns:
            Env: The updated environment with the new binding.

        Example:
            env.bind("x", 10)  # Binds 'x' to the value 10 in the environment.
        """
        self[name] = value
        return self

    def extend(self, name: str, value: tuple) -> Env:
        """
        Returns a new environment that is an extension of the current one, with the addition of a new variable binding.

        This method creates a fresh environment that includes all the bindings from the current environment
        plus the new binding `name → value`.

        Args:
            name (str): The name of the variable to bind in the new environment.
            value (tuple): The value (or values) to bind to the variable.

        Returns:
            Env: A new environment with the added binding.

        Example:
            new_env = env.extend("y", (5,))  # Creates a new environment with 'y' bound to (5,) in addition to the original bindings.
        """
        new_env = Env(self)
        new_env.data[name] = value
        return new_env

    @classmethod
    def ensure(cls, value: Env | dict | None) -> Env | None:
        """
        Ensures that the provided value is either an `Env` instance or can be converted to one.

        If the provided value is already an `Env` instance, it returns it unchanged.
        If the value is a dictionary, it wraps it in an `Env` object.
        If the value is `None`, it returns `None`.

        Args:
            value (Env | dict | None): The value to check and convert if necessary.

        Returns:
            Env | None: The `Env` object, or `None` if the input is `None`.

        Example:
            env = Env.ensure({"a": (1,)})  # Converts the dictionary to an Env object.
        """
        return cls(*value) if isinstance(value, dict) else value

    @staticmethod
    def combine(left: Env | dict | None, right: Env | dict | None) -> Env | None:
        """
        Combines two environments or dictionaries into one.

        If either `left` or `right` is `None`, the function returns `None`.
        Otherwise, it merges the two environments and returns a new `Env` object.

        Args:
            left (Env | dict | None): The first environment or dictionary to combine.
            right (Env | dict | None): The second environment or dictionary to combine.

        Returns:
            Env | None: The combined `Env` object, or `None` if either input is `None`.

        Example:
            combined_env = Env.combine(env1, env2)  # Combines env1 and env2 into a new environment.
        """
        if left is None or right is None:
            return None
        return Env({**left, **right})
