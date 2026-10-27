# javhar-util

Small, general-purpose Python utilities. Dependency-free at its core: modules that need
third-party packages will sit behind optional extras.

## Immutable collections

`ZVec`, `ZSet` and `ZMap` are immutable, hashable counterparts to `list`, `set` and
`dict`. They are deeply immutable (construction fails if any element is unhashable),
cache their hash at construction, and follow the read-only interface of their mutable
counterparts.

```python
from javhar_util.immutables import ZMap, ZSet, ZVec

ranks = ZVec([3, 1, 2])
seen = ZSet(["a", "b"])
scores = ZMap({"a": 1, "b": 2})

cache = {ranks: "hashable, so usable as a key"}
```

See the docstring of `javhar_util.immutables` for the motivation and the alternatives
considered.

## Installation

```
pip install "javhar-util @ git+https://github.com/javhar-hex/util"
```

Requires Python 3.11 or later.

## Development

```
pip install -e ".[dev]"
pytest
mypy src tests
ruff check && ruff format --check
```

## Licence

Apache License 2.0; see `LICENSE`.
