"""Layer classifier: assigns UI / API / DB / Util labels to module names."""

import re
from pathlib import Path

# Patterns for each layer (checked in order)
_LAYER_RULES = [
    ("UI",   re.compile(r"component|view|page|screen|widget|jsx|tsx|render|ui", re.I)),
    ("API",  re.compile(r"api|service|client|request|http|rest|graphql|grpc|endpoint", re.I)),
    ("DB",   re.compile(r"db|dao|repository|model|orm|schema|migration|database|sql|mongo|redis", re.I)),
    ("Util", re.compile(r"util|helper|tool|common|shared|lib|mixin|decorator|middleware", re.I)),
]

_DEFAULT_LAYER = "App"


def classify_layer(name: str, filepath: str = "") -> str:
    """Return the layer label for a module *name* (and optional file path).

    The function first checks the *filepath* stem / path segments, then
    falls back to the bare *name* string.
    """
    candidates = [name]
    if filepath:
        p = Path(filepath)
        candidates += list(p.parts) + [p.stem]

    for candidate in candidates:
        for layer, pattern in _LAYER_RULES:
            if pattern.search(candidate):
                return layer

    return _DEFAULT_LAYER
