from collections import deque
import functools
import typing as t


_Callable_t = t.TypeVar("_Callable_t")


def transaction(callable: _Callable_t) -> _Callable_t:
    """Wrapper to define a transaction where some reversible process can be
    processed.

    This decorator tracks reversible methods in given callable and execute
    the backward processes if any errors occur in the callable.

    Args:
        callable: Callable to be wrapped.

    Returns:
        Wrapped callable.
    """
    stack: t.Deque[t.Tuple[t.Callable, t.Tuple[t.Any, ...]]] = deque()

    @functools.wraps(callable)
    def _callable(*args, **kwargs):
        __reversible_stack__ = stack

        try:
            return_value = callable(*args, **kwargs)
        except Exception as e:
            while len(stack):
                backward, args_ = stack.pop()
                backward(*args_)
            raise e
        else:
            return return_value

    return _callable
