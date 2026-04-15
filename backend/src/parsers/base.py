"""Base data classes for sequence diagram parsing."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CallInfo:
    """Represents a single function/method call."""

    caller: str
    callee: str
    function: str
    file: str
    line: int
    layer_caller: Optional[str] = None
    layer_callee: Optional[str] = None


@dataclass
class SequenceData:
    """Aggregated sequence data for a parsed project."""

    calls: List[CallInfo] = field(default_factory=list)
    files: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def add_call(self, call: CallInfo) -> None:
        self.calls.append(call)

    def add_file(self, path: str) -> None:
        if path not in self.files:
            self.files.append(path)

    def add_error(self, message: str) -> None:
        self.errors.append(message)
