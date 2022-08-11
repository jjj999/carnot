import pytest
from carnot import (
    reversible_function,
    reversible_method,
    transaction,
)


class Counter:

    INITIAL_VALUE = 0

    def __init__(self) -> None:
        self._count = self.INITIAL_VALUE

    @property
    def count(self) -> None:
        return self._count

    @reversible_method
    def add(self, count: int) -> None:
        self._count += count
        Counter.add.set_args(self, count)

    @add.backward
    def _add(self, count: int) -> None:
        self._count -= count

    @reversible_method
    def increment_count(self) -> int:
        self._count += 1

        Counter.increment_count.set_args(self)
        return self._count

    @increment_count.backward
    def _increment_count(self) -> None:
        self._count -= 1


@reversible_function
def times(counter: Counter, multiple: int) -> None:
    counter.add(counter.count * (multiple - 1))
    times.set_args(counter, multiple)


@times.backward
def _times(counter: Counter, multiple: int) -> None:
    counter.add(- counter.count * (multiple - 1))


@transaction
def reversible_process(counter: Counter) -> None:
    counter.increment_count()
    counter.add(3)
    times(counter, 10)
    raise ValueError


def test_reversible() -> None:
    counter = Counter()

    with pytest.raises(ValueError):
        reversible_process(counter)

    assert counter.count == Counter.INITIAL_VALUE
