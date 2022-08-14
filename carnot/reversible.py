from __future__ import annotations
import functools
import inspect
import typing as t

from typing_extensions import (
    Concatenate,
    ParamSpec,
)


_P = ParamSpec("_P")
_Q = ParamSpec("_Q")
_R = t.TypeVar("_R")


class reversible_function(t.Generic[_P, _Q, _R]):

    def __init__(
        self,
        f_forward: t.Callable[_P, _R],
        f_backward: t.Optional[t.Callable[_Q, None]] = None,
    ) -> None:
        self.__doc__ = f_forward.__doc__
        self._f_forward = f_forward
        self._f_backward = f_backward
        self._args: t.Tuple[t.Any, ...] = ()

    def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _R:
        return_value = self._f_forward(*args, **kwargs)

        if self._f_backward is not None:
            for record in inspect.stack():
                if "__reversible_stack__" in record.frame.f_locals:
                    stack = record.frame.f_locals["__reversible_stack__"]
                    stack.append((self._f_backward, self._args))
                    break

        return return_value

    def backward(
        self,
        f_backward: t.Callable[_Q, None],
    ) -> reversible_function:
        """Registers a function for backward process.

        Args:
            f_backward: Function for backward process.

        Returns:
            `reversible_function` itself.
        """
        self._f_backward = f_backward
        return self

    def set_args(self, *args: t.Any) -> None:
        """Sets arguments for the backward function.

        Args:
            *args: Arguments given to the backward function.
        """
        self._args = args

    def get_forward(self) -> t.Callable[_P, _R]:
        """Returns the forward function.

        Returns:
            Registered forward function.
        """
        return self._f_forward

    def get_backward(self) -> t.Callable[_Q, None]:
        """Returns the backward function.

        Returns:
            Registered backward function.
        """
        return self._f_backward


_Object_t = t.TypeVar("_Object_t")


class reversible_method(t.Generic[_Object_t, _P, _Q, _R]):
    """Descriptor for reversible methods.

    This descriptor can be applied to reversible methods, whose processes are
    not unidirectional. Using this descriptor, developers can define the
    forward process and backward process, the former is processed first in a
    transaction and the latter is processed if the transaction failes.

    Transactions in `reversible` are defined using `reversible.transaction`.
    For more information about transactions, see the documentation.
    """

    def __init__(
        self,
        f_forward: t.Callable[Concatenate[_Object_t, _P], _R],
        f_backward: t.Optional[
            t.Callable[Concatenate[_Object_t, _Q], None]
        ] = None,
    ) -> None:
        """
        Args:
            f_forward: Function for forward process.
            f_backward: Function for backward process.
        """
        self.__doc__ = f_forward.__doc__
        self._f_forward = f_forward
        self._f_backward = f_backward
        self._args: t.Tuple[t.Any, ...] = ()

    @t.overload
    def __get__(
        self,
        instance: None,
        owner: t.Optional[t.Type[_Object_t]] = None,
    ) -> reversible_method:
        ...

    @t.overload
    def __get__(
        self,
        instance: _Object_t,
        owner: t.Optional[t.Type[_Object_t]] = None,
    ) -> t.Callable[_P, _R]:
        ...

    def __get__(self, instance, owner = None):
        if instance is None:
            return self

        @functools.wraps(self._f_forward)
        def _callback(*args, **kwargs):
            return_value = self._f_forward(instance, *args, **kwargs)

            if self._f_backward is not None:
                for record in inspect.stack():
                    if "__reversible_stack__" in record.frame.f_locals:
                        stack = record.frame.f_locals["__reversible_stack__"]
                        stack.append((self._f_backward, self._args))
                        break

            return return_value

        return _callback

    def backward(
        self,
        f_backward: t.Callable[Concatenate[_Object_t, _Q], None],
    ) -> reversible_method:
        """Registers a function for backward process.

        Args:
            f_backward: Function for backward process.

        Returns:
            `reversible_method` itself.
        """
        self._f_backward = f_backward
        return self

    def set_args(self, *args: t.Any) -> None:
        """Sets arguments for the backward function.

        Args:
            *args: Arguments given to the backward function.
        """
        self._args = args

    def get_forward(self) -> t.Callable[[Concatenate[_Object_t, _P], _R]]:
        """Returns the forward function.

        Returns:
            Registered forward function.
        """
        return self._f_forward

    def get_backward(self) -> t.Callable[[Concatenate[_Object_t, _Q], None]]:
        """Returns the backward function.

        Returns:
            Registered backward function.
        """
        return self._f_backward
