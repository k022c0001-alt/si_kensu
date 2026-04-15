"""Export sequence data as JSON or Mermaid sequenceDiagram syntax."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from ..parsers.base import SequenceData


class SequenceExporter:
    """Convert :class:`SequenceData` to JSON or Mermaid output."""

    # ------------------------------------------------------------------ #
    # JSON
    # ------------------------------------------------------------------ #

    def to_json(self, data: SequenceData, indent: int = 2) -> str:
        """Return a JSON string representing *data*."""
        payload = {
            "files": data.files,
            "errors": data.errors,
            "calls": [
                {
                    "caller": c.caller,
                    "callee": c.callee,
                    "function": c.function,
                    "file": c.file,
                    "line": c.line,
                    "layer_caller": c.layer_caller,
                    "layer_callee": c.layer_callee,
                }
                for c in data.calls
            ],
        }
        return json.dumps(payload, ensure_ascii=False, indent=indent)

    def save_json(self, data: SequenceData, path: str) -> None:
        """Write JSON output to *path*."""
        Path(path).write_text(self.to_json(data), encoding="utf-8")

    # ------------------------------------------------------------------ #
    # Mermaid
    # ------------------------------------------------------------------ #

    def to_mermaid(self, data: SequenceData) -> str:
        """Return a Mermaid ``sequenceDiagram`` string."""
        lines = ["sequenceDiagram"]
        seen: set = set()

        for call in data.calls:
            caller = self._sanitize(call.caller or "App")
            callee = self._sanitize(call.callee or call.caller or "App")
            label = call.function

            # Declare participants once
            for participant in (caller, callee):
                if participant not in seen:
                    lines.append(f"    participant {participant}")
                    seen.add(participant)

            lines.append(f"    {caller}->>+{callee}: {label}()")
            lines.append(f"    {callee}-->>-{caller}: return")

        return "\n".join(lines)

    def save_mermaid(self, data: SequenceData, path: str) -> None:
        """Write Mermaid output to *path*."""
        Path(path).write_text(self.to_mermaid(data), encoding="utf-8")

    # ------------------------------------------------------------------ #

    @staticmethod
    def _sanitize(name: str) -> str:
        """Replace characters that Mermaid cannot handle in participant names."""
        return name.replace("<", "").replace(">", "").replace('"', "").replace(":", "_")
