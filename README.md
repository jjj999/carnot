# carnot

`carnot` is a module that enables reversible transactions for general purposes. Reversible transactions may make your codes simpler and have better readability inspite of complicated logics.

## Installing

- Python >= 3.8

```
python -m pip install carnot
```

## Usage

```python
from carnot import reversible_function, transaction

count = 0

@reversible_function
def add(num: int) -> None:
    global count
    count += num
    add.set_args(num)

@add.backward
def _add(num: int) -> None:
    global count
    count -= num

@transaction
def add_and_emit_error() -> None:
    add(2)
    raise Exception

if __name__ == "__main__":
    try:
        add_and_emit_error()
    except:
        pass
    finally:
        print(count)    # 0
```
