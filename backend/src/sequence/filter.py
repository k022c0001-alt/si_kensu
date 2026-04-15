"""Filter engine for sequence diagram data."""

from __future__ import annotations

from typing import List, Optional, Set

from ..parsers.base import CallInfo, SequenceData


class SequenceFilter:
    """Apply various filter modes to a :class:`SequenceData` object."""

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def filter(
        self,
        data: SequenceData,
        mode: str = "detail",
        include_layers: Optional[List[str]] = None,
        exclude_layers: Optional[List[str]] = None,
        include_callers: Optional[List[str]] = None,
        deduplicate: bool = True,
    ) -> SequenceData:
        """Return a filtered copy of *data*.

        Parameters
        ----------
        mode:
            ``"detail"``   – keep all calls (default).
            ``"summary"``  – collapse duplicate caller→function pairs.
            ``"custom"``   – apply include/exclude layer lists.
        include_layers:
            If provided, only keep calls where **caller** layer is in the list.
        exclude_layers:
            If provided, drop calls where **caller** or **callee** layer is in
            the list.
        include_callers:
            If provided, only keep calls whose ``caller`` matches one of these.
        deduplicate:
            When ``True`` remove identical (caller, callee, function) triples.
        """
        calls = list(data.calls)

        if mode == "summary":
            calls = self._summarize(calls)
        elif mode == "custom":
            calls = self._apply_layer_filter(calls, include_layers, exclude_layers)

        if include_callers:
            caller_set: Set[str] = set(include_callers)
            calls = [c for c in calls if c.caller in caller_set]

        if deduplicate:
            calls = self._deduplicate(calls)

        result = SequenceData(files=list(data.files), errors=list(data.errors))
        result.calls = calls
        return result

    # ------------------------------------------------------------------ #
    # Private helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _summarize(calls: List[CallInfo]) -> List[CallInfo]:
        """Keep one representative call per (caller, function) pair."""
        seen: Set[tuple] = set()
        out: List[CallInfo] = []
        for c in calls:
            key = (c.caller, c.function)
            if key not in seen:
                seen.add(key)
                out.append(c)
        return out

    @staticmethod
    def _apply_layer_filter(
        calls: List[CallInfo],
        include: Optional[List[str]],
        exclude: Optional[List[str]],
    ) -> List[CallInfo]:
        inc = set(include) if include else None
        exc = set(exclude) if exclude else set()
        out: List[CallInfo] = []
        for c in calls:
            if inc and c.layer_caller not in inc:
                continue
            if c.layer_caller in exc or c.layer_callee in exc:
                continue
            out.append(c)
        return out

    @staticmethod
    def _deduplicate(calls: List[CallInfo]) -> List[CallInfo]:
        seen: Set[tuple] = set()
        out: List[CallInfo] = []
        for c in calls:
            key = (c.caller, c.callee, c.function)
            if key not in seen:
                seen.add(key)
                out.append(c)
        return out
