# CLAUDE.md — Project Coding Standards

These are non-negotiable style rules, not suggestions. Follow them for every
file you write or edit in this repository, including tests. If a request
would require violating one of these to satisfy some other constraint, stop
and flag the conflict rather than silently picking one.

## Overarching philosophy

Write code so that someone — usually me, three months from now — can look at
one class or module in isolation and understand it without reading anything
else. And write it so the caller *cannot* misuse it, not merely so that
misuse would be noticed.

- `DbConnector.open()` returns a `DbConnection`; only `DbConnection` has
  `query()`. There is no way to query without having opened a connection.
- A `Probability` cannot hold `1.7`. Construction itself enforces the
  invariant — it isn't a float that happens to get checked somewhere else.

If code needs a comment to explain *what* it does, rewrite it until it
doesn't. Comments are for the rare "gee, why didn't they just do it the
obvious way" programmer's note — not for restating the code.

## Composition over inheritance

Default to composition. Inheritance requires a strong, explicit justification
— don't reach for it out of habit. Prefer protocols/interfaces over base
classes when you need polymorphism.

## Immutability

Objects are immutable by default. Mutation is allowed only when strictly
needed for performance, or inside a `Builder`.

- Use `ZVec`, `ZSet`, `ZMap` for variable-length homogeneous collections —
  never a `tuple` as a stand-in for an immutable list, and never bare
  `frozenset`/`immutables.Map`. A tuple is a fixed-length, mixed-type
  container; reserve it for genuinely fixed-shape data (coordinates, a
  key-value pair returned from a single call site), never for a list.
- Use `@dataclass(frozen=True)` for value objects.
- If a method appears to need to mutate `self`, first ask whether it should
  instead return a new instance.

## Return a generator only for a one-shot, immediately-consumed result

If a method's result will be iterated exactly once, immediately, and never
retained — never stored, indexed, re-iterated, or compared — prefer
returning an `Iterator` (typically a generator, via `yield`) over eagerly
building a `list` or other container. It avoids a pointless intermediate
allocation and the type itself documents the single-pass contract.

- This is *not* a blanket "iterable is always better than a concrete
  container" rule. A generator isn't a value — it carries hidden mutable
  cursor state, so `len()`, indexing, and a second `for` loop all either
  fail or silently do nothing (an exhausted generator just yields
  nothing, with no error). That's a real footgun, and it's in tension
  with this codebase's immutable-by-default stance.
- If the result is a value in its own right — something a caller might
  hold onto, inspect more than once, or compare for equality — return an
  immutable collection (`ZVec`/`ZSet`/`ZMap`), not a generator and not a
  bare `list`.
- Example: `CurveStyle.visible_series()` used to build and return a
  `list[TimeSeries[float]]`, but its only caller consumes it once, inline,
  in a nested comprehension, and never keeps the result around. Rewriting
  it as a generator (`Iterator[TimeSeries[float]]`, built with `yield`)
  dropped the intermediate list with no loss of correctness.

## Zero-argument methods on immutable classes are properties

Because instances are immutable, a method that takes no arguments beyond
`self` always returns the same answer for the same object. Make it a
`@property`. The caller shouldn't need to know or care whether the value
was precomputed at construction or is being derived on access — it should
just read like an attribute: `foo.bar`, not `foo.get_bar()` or `foo.bar()`.

- If the computation is expensive, use `@cached_property` instead of
  `@property`, and pair it with lazy construction where useful — there's
  no need to pay for an expensive derived value until something actually
  asks for it.
- This does not apply to methods that take arguments (`foo.plus(bar)`
  stays a method), and it does not license mutation — a cached property
  still must not change the value it returns across calls.

## No dependency cycles — the whole codebase is a strict DAG

- **Classes**: no cycles between classes.
- **Packages**: `foo` may depend on `foo.bar`, never the reverse.
  Dependencies are inherited upward through the package hierarchy — if
  anything under `foo` depends on anything under `bar`, then `foo` depends
  on `bar`, and nothing under `bar` may ever depend on anything under `foo`.
- **Methods within a class**: should be topologically sortable top-to-bottom.
  Mutual recursion is the only acceptable exception, and only when genuinely
  needed.
- **Clustering, when the call graph doesn't decide it.** PEP 8 has no rule
  here, but group methods by role, top to bottom: `__post_init__` (or
  `__init__`, on a non-dataclass) first — it's construction itself, not a
  peer of the other dunders, so it goes ahead of even the alternative
  constructors below it — then alternative-constructor classmethods
  (`.of()`, `.of_raw()`, ...), then other dunders (`__add__`, `__float__`,
  ...), then properties/`cached_property`, then public methods, then
  private (`_`-prefixed) methods. The topological rule above still breaks
  ties *within* a cluster; the cluster order itself is just this
  convention.
- **No unnecessary edges.** If a function needs both a `Foo` and a `Bar`,
  it does not belong on `Foo` (`foo.plus_bar(bar)`) or on `Bar` — that
  creates a dependency neither class actually needs, and it's arbitrary
  which one "owns" it. Put it in a higher-level module that already depends
  on both.

## Semantic types, not raw primitives or anonymous tuples

- Never return an anonymous `tuple[float, float]` and make the caller
  remember which element is which. Return a named class instead.
- Wrap *any* primitive that has a distinguishing trait — not just IDs.
  A primitive is a wrapping candidate if any of these are true:
  - **Not every value of the primitive is valid.** `Probability` cannot be
    `<0` or `>1` — enforce it in construction, not in a comment or a
    downstream check.
  - **Mixing it with another value of the same primitive type would be a
    bug.** `get_id() -> PersonId`, not `get_id() -> long` — it should be
    structurally impossible to pass a `PersonId` where an `OrderId` is
    expected.
  - **The unit could be ambiguous.** This is the Mars Climate Orbiter
    case: a bare `float` for a physical quantity invites someone to pass
    metres where kilometres were expected, and the type checker can't
    catch it. `price_in_cents` (a suffixed name on a primitive) is the
    bare minimum; the real fix is a class:

    ```python
    d1 = Distance.of(123, METRES)
    d2 = Distance.of(1.23, KILOMETRES)
    d1 < d2                # comparisons and arithmetic happen on the
                            # Distance itself — callers shouldn't need
                            # to reach for .metres or .kilometres
    ```

    Unit values (`METRES`, `KILOMETRES`, ...) are members of a
    `DistanceUnit` enum, not hardcoded strings — but re-export them as
    module-level constants (`METRES = DistanceUnit.METRES`, etc.) so call
    sites can write `Distance.of(123, METRES)` instead of the more
    verbose `Distance.of(123, DistanceUnit.METRES)`. They're still real
    enum members with full type safety — just imported by their short
    name (`from units import METRES, KILOMETRES`) instead of qualified
    through the enum class. Use this pattern anywhere a unit, currency,
    or similar small closed set of tags would otherwise repeat a
    qualified enum name at every call site.

## Single responsibility

If a class is accumulating unrelated responsibilities, split it.

- Rule of thumb: **~200 lines per file**, **~25 lines per method**. Going
  over either is a signal — not an automatic violation, but a prompt to ask
  whether the class/method is doing more than one job and should be
  decomposed into smaller pieces called from a coordinating method.

## DRY

No value or piece of logic is defined in more than one place. If you're
about to copy a constant, a formula, or a branch of logic, extract it
instead.

## Early return vs. explicit `else`

`if condition: return foo` followed by an unindented `return bar` is
equivalent to adding `else: return bar` — the question is which one to
write.

- **Guard clause, then the rest of the function**: no `else`. `if not
  series: raise ValueError(...)` followed by the real body isn't a peer
  of that body — it's a precondition being ruled out before the function
  gets on with its actual job. An `else` here would just wrap "the rest
  of the function" in a redundant indent.
- **A deliberate two-way (or N-way) dispatch that *is* the function's
  whole body**: keep the `else`. When both branches are equally-weighted
  computations of the same thing — e.g. `_straight_mean` vs.
  `_weighted_mean` — the condition doesn't have a privileged "true" case
  and a fallthrough; it's arbitrary which side gets written as the `if`
  and which as the `else` (the condition could just as well have been
  negated, swapping which branch "falls through"). Writing `else` makes
  that symmetry visible instead of implying one branch is the special
  case and the other is just whatever's left.

## Strict typing

- Full type annotations everywhere, checked (mypy `--strict` or equivalent
  — no unchecked corners).
- No duck typing. Use `Protocol` for structural interfaces where the
  concrete implementation shouldn't be hard-coded.
- No `# type: ignore`, no bare `# noqa`, no suppressing a checker instead of
  fixing what it's flagging. If a suppression is genuinely warranted, that's
  rare enough to need a one-line programmer's note explaining why.

## Construction: factories and builders

- Never a wall of positional args: `Foo(3.14, 81, True, "hello", ...)`.
  Use named arguments at minimum.
- If a constructor could leave the object in an invalid state, don't expose
  the constructor directly — expose a `classmethod` factory instead:
  `Foo.of(...)`, not `staticmethod`. Validation belongs in `__post_init__`,
  but the factory is what makes the *invalid path* awkward to reach at all.
- `__post_init__` only validates — it never normalizes. If a value could be
  brought into a valid shape (sorting a sequence, canonicalizing a case,
  rounding to a supported precision), that normalization belongs in the
  `.of()` factory or `Builder`, not in `__post_init__`. `__post_init__`'s
  job is to reject whatever the factory didn't already fix up — it doesn't
  get to silently correct the object's state on the way in. Someone who
  bypasses the factory and calls the constructor directly is on the hook
  for handing it already-valid state; `__post_init__` exists to catch them
  if they don't, not to clean up after them.
- If an object has many optional parameters, or needs to be assembled
  piece by piece (e.g. a map built up one entry at a time), give it a
  `Builder` — typically a mutable shadow of the same class, holding plain
  `list`/`dict` internally, that converts to `ZVec`/`ZMap` on `.build()`.

  ```python
  foo = (
      Foo.Builder()
      .add_bar(3.14)
      .add_baz(81)
      .disable_qux()
      .build()
  )
  ```

## Default values must be "natural," not use-case-specific

A default value is only appropriate when it's a value nearly any caller
would want absent a specific reason to override it — the kind of thing you
could justify from first principles, not from taste. If the "right" value
could reasonably differ from one deployment, app, or user to the next, it
isn't a default — it's configuration, and the parameter should be required.

- **Natural/universal**: `None` for an optional/absent value, an identity
  element (`0`, an empty collection), a numeric tolerance, or a
  rendering-mechanics knob with a sensible one-size-fits-all answer — e.g.
  `ChartStyle.x_padding_fraction=0.005`, a small margin so plotted points
  don't touch the axis spine, comparable to matplotlib's own default axis
  margins.
- **Use-case-specific**: colours, a figure's physical size in inches, a
  particular set of gridline tiers, a particular moving-average window
  length — anything that's presentation, branding, or personal-preference
  data. These belong in the caller's config (a notebook, a Streamlit app's
  settings), not baked into library code, even as a "sensible-sounding"
  default. There's nothing more natural about 17.92 inches than about a
  specific shade of blue — both were removed from `ChartStyle` in favor of
  requiring the caller to supply them.
- The test: could you defend this exact value to a stranger using only the
  mechanics of what it's used for, with no appeal to "it looked right" or
  "that's what we use"? If not, don't default it — require it.

## Testing

Thorough unit tests for every module — enough that a change anywhere gives
real confidence nothing broke elsewhere. Tests follow the same standards as
production code (typed, DRY, no cycles, short and single-purpose).

## Quick self-check before finishing a change

- Any new inheritance? Could it have been composition instead?
- Any raw `tuple`, `list`, `dict`, or `set` where `ZVec`/`ZSet`/`ZMap` or a
  frozen dataclass belongs?
- Any new package-level or class-level dependency edge — and does it point
  the direction it should?
- Any primitive that's really a semantic type in disguise — an id, a
  bounded value, or a value with a unit/currency that could be confused
  with a different scale or a different kind of quantity?
- Any zero-argument method on an immutable class that should be a
  `@property` (or `@cached_property` if it's expensive)?
- Any file pushing past ~200 lines, or method past ~25?
- Any duplicated logic or constant?
- Any missing type annotation, suppressed type error, or duck-typed
  interface?
- Any constructor that permits an invalid state without a factory guarding it?
- Any default value that's really use-case-specific data (a colour, a size,
  a window length) rather than a natural/universal one?
- Does every new piece of logic have a test?
