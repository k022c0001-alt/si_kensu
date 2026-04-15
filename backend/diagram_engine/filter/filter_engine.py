"""Class diagram filter engine."""

from __future__ import annotations

from typing import List, Optional, Set

from ..parser.project_parser import ProjectData
from ..parser.py_parser import ClassInfo
from ..parser.js_parser import ComponentInfo


class ClassDiagramFilter:
    """Filter :class:`ProjectData` for class diagram rendering.

    Modes
    -----
    detail   – keep all members, including private ones.
    overview – hide private members; show only public interface.
    """

    def filter(
        self,
        data: ProjectData,
        mode: str = "detail",
        languages: Optional[List[str]] = None,
        exclude_private: Optional[bool] = None,
    ) -> ProjectData:
        """Return a filtered copy of *data*.

        Parameters
        ----------
        mode:
            ``"detail"`` or ``"overview"``.
        languages:
            If set, only include classes/components from these languages
            (``"python"``, ``"javascript"``).
        exclude_private:
            Override private-member exclusion.  Defaults to ``True`` for
            *overview* mode, ``False`` for *detail* mode.
        """
        hide_private = (
            exclude_private
            if exclude_private is not None
            else (mode == "overview")
        )
        lang_filter: Optional[Set[str]] = set(languages) if languages else None

        filtered_classes = [
            self._filter_class(c, hide_private)
            for c in data.classes
            if lang_filter is None or c.language in lang_filter
        ]

        filtered_components = [
            self._filter_component(comp, hide_private)
            for comp in data.components
            if lang_filter is None or comp.language in lang_filter
        ]

        from ..parser.project_parser import ProjectData as PD

        result = PD(
            classes=filtered_classes,
            components=filtered_components,
            dependencies=dict(data.dependencies),
            errors=list(data.errors),
        )
        return result

    # ------------------------------------------------------------------ #

    @staticmethod
    def _filter_class(cls: ClassInfo, hide_private: bool) -> ClassInfo:
        if not hide_private:
            return cls
        from ..parser.py_parser import ClassInfo as CI, MethodInfo, PropertyInfo

        props = [p for p in cls.properties if p.access != "private"]
        methods = [m for m in cls.methods if m.access != "private"]
        result = CI(
            name=cls.name,
            file=cls.file,
            bases=list(cls.bases),
            language=cls.language,
        )
        result.properties = props
        result.methods = methods
        return result

    @staticmethod
    def _filter_component(comp: ComponentInfo, hide_private: bool) -> ComponentInfo:
        # React components do not have private members in the same sense;
        # return as-is.
        return comp


def to_mermaid_class_diagram(data: ProjectData) -> str:
    """Convert filtered :class:`ProjectData` into a Mermaid ``classDiagram``."""
    lines = ["classDiagram"]

    for cls in data.classes:
        lines.append(f"    class {cls.name} {{")
        for prop in cls.properties:
            symbol = _access_symbol(prop.access)
            type_str = f" {prop.type_hint}" if prop.type_hint else ""
            lines.append(f"        {symbol}{prop.name}{type_str}")
        for method in cls.methods:
            symbol = _access_symbol(method.access)
            params = ", ".join(method.params)
            ret = f" {method.return_type}" if method.return_type else ""
            lines.append(f"        {symbol}{method.name}({params}){ret}")
        lines.append("    }")

    for comp in data.components:
        lines.append(f"    class {comp.name} {{")
        lines.append(f"        <<component>>")
        for prop in comp.props:
            type_str = f" {prop.type_hint}" if prop.type_hint else ""
            lines.append(f"        +{prop.name}{type_str}")
        for hook in comp.hooks:
            lines.append(f"        +{hook.name}()")
        lines.append("    }")

    # Inheritance
    for cls in data.classes:
        for base in cls.bases:
            lines.append(f"    {base} <|-- {cls.name}")

    # Component dependencies (imports of local files)
    for comp in data.components:
        for imp in comp.imports:
            if not imp.startswith("."):
                continue
            # Map import path to component name if possible
            imported_name = _import_to_name(imp)
            if imported_name:
                lines.append(f"    {comp.name} ..> {imported_name} : uses")

    return "\n".join(lines)


def _access_symbol(access: str) -> str:
    return {
        "public": "+",
        "protected": "#",
        "private": "-",
    }.get(access, "+")


def _import_to_name(imp: str) -> str:
    """Best-effort: extract a PascalCase name from an import path like './MyComp'."""
    stem = imp.rstrip("/").split("/")[-1]
    # Remove extension if any
    if "." in stem:
        stem = stem.rsplit(".", 1)[0]
    # Return only if it looks like a component name
    if stem and stem[0].isupper():
        return stem
    return ""
