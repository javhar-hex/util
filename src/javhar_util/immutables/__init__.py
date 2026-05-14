"""
Immutable collection types for Python.

ZList, ZMap, and ZSet are immutable, hashable counterparts to Python's list, dict, and
set. They are designed for codebases that favour immutability throughout. All three
collections:
- Are deeply immutable: construction fails if any element or key/value is not itself
  hashable, ensuring immutability all the way down the object graph.
- Cache their hash at construction time, so repeated hashing is O(1).
- Follow the same interface as their mutable counterparts, making them drop-in
  replacements for read-only use.

Motivations:
- Python's tuple[T, ...] can be used as an immutable list, but has two drawbacks:
  - As the type hint indicates it is a semantic misuse: conceptually a tuple is a
    fixed-length heterogeneous structure, where a ZList is meant to be a variable-length
    homogenous collection.
  - Whereas tuples are immutable, they are not deeply immutable. For instance, a tuple
    can contain a list, and that list can be mutated. Calling hash() on such a tuple will
    raise a TypeError.
- Python's frozenset exists, and ZSet is just a lightweight wrapper around it that adds
  the precomputed hash. 
- No equivalent for ZMap exists in Python.
- At construction time, deep immutability is ensured by attempting to compute a hash
  value. Since the hash value is then available anway, it is cached for future use.

Alternatives:
- Immutables provides Immutables.Map. Contrary to what its name suggest, the library does
  not contain anything else.
- frozendict is an external library.
- pyrsistent provides pvector, pmap, and pset, but is less lightweight as the library is
  geared towards persistance rather than immutability, and as such it contains much
  additional functionality. Its pvector is less effcient with hashing.
"""