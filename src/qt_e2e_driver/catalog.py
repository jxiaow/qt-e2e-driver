from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from difflib import get_close_matches
from typing import Any

from .errors import (
    DuplicateAliasError,
    EmptyAliasCatalog,
    InvalidAliasCatalog,
    UnknownAliasInCatalog,
)


@dataclass(frozen=True)
class AliasEntry:
    alias: str
    object_name: str
    page: str = ""
    owner: str = ""
    role: str = ""
    class_hint: str = ""
    required: bool = False
    deprecated: bool = False
    description: str = ""
    hit_targets: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "AliasEntry":
        alias = str(data.get("alias", "")).strip()
        object_name = str(data.get("objectName", data.get("object_name", ""))).strip()
        return cls(
            alias=alias,
            object_name=object_name,
            page=str(data.get("page", "")),
            owner=str(data.get("owner", "")),
            role=str(data.get("role", "")),
            class_hint=str(data.get("classHint", data.get("class_hint", ""))),
            required=_parse_bool(data, "required", alias),
            deprecated=_parse_bool(data, "deprecated", alias),
            description=str(data.get("description", "")),
            hit_targets=_parse_hit_targets(data, alias),
        )


class AliasCatalog:
    def __init__(self, entries: Iterable[AliasEntry]) -> None:
        self._entries: dict[str, AliasEntry] = {}
        for entry in entries:
            if not entry.alias:
                raise InvalidAliasCatalog("alias catalog contains an entry without alias")
            if not entry.object_name:
                raise InvalidAliasCatalog(f"alias {entry.alias} is missing objectName")
            if entry.alias in self._entries:
                raise DuplicateAliasError(f"duplicate alias in catalog: {entry.alias}")
            self._entries[entry.alias] = entry
        if not self._entries:
            raise EmptyAliasCatalog("list-aliases returned an empty alias catalog")

    @classmethod
    def from_payload(cls, payload: Any) -> "AliasCatalog":
        if isinstance(payload, Mapping):
            if "aliases" not in payload:
                raise InvalidAliasCatalog("alias catalog payload is missing aliases")
            payload = payload.get("aliases", ())
        if isinstance(payload, (str, bytes)) or not isinstance(payload, Iterable):
            raise InvalidAliasCatalog("alias catalog aliases must be a list")

        entries: list[AliasEntry] = []
        for index, item in enumerate(payload):
            if not isinstance(item, Mapping):
                raise InvalidAliasCatalog(f"alias catalog entry {index} must be an object")
            entries.append(AliasEntry.from_mapping(item))
        return cls(entries)

    def __contains__(self, alias: str) -> bool:
        return alias in self._entries

    def __len__(self) -> int:
        return len(self._entries)

    def aliases(self) -> tuple[str, ...]:
        return tuple(sorted(self._entries))

    def get(self, alias: str) -> AliasEntry:
        try:
            return self._entries[alias]
        except KeyError as exc:
            available = ", ".join(self.aliases())
            message = f"UNKNOWN_ALIAS_IN_CATALOG: {alias}; available aliases: {available}"
            suggestions = get_close_matches(alias, self.aliases(), n=3, cutoff=0.65)
            if suggestions:
                message += f"; did you mean: {', '.join(suggestions)}"
            raise UnknownAliasInCatalog(message) from exc


class UiAliases:
    def __init__(self, catalog: AliasCatalog, prefix: str = "") -> None:
        self._catalog = catalog
        self._prefix = prefix

    def __getattr__(self, name: str) -> "UiAliases | str":
        alias = f"{self._prefix}.{name}" if self._prefix else name
        if alias in self._catalog:
            return alias
        has_children = any(item.startswith(alias + ".") for item in self._catalog.aliases())
        if has_children:
            return UiAliases(self._catalog, alias)
        self._catalog.get(alias)
        return alias

    def __dir__(self) -> list[str]:
        names = set(super().__dir__())
        prefix = self._prefix + "." if self._prefix else ""
        for alias in self._catalog.aliases():
            if not alias.startswith(prefix):
                continue
            remainder = alias[len(prefix) :]
            names.add(remainder.split(".", 1)[0])
        return sorted(names)


def _parse_bool(data: Mapping[str, Any], field: str, alias: str) -> bool:
    if field not in data:
        return False

    value = data[field]
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "y", "on"}:
            return True
        if normalized in {"false", "0", "no", "n", "off"}:
            return False

    label = alias or "<missing alias>"
    raise InvalidAliasCatalog(f"alias {label} has invalid {field}: {value!r}")


def _parse_hit_targets(data: Mapping[str, Any], alias: str) -> tuple[str, ...]:
    value = data.get("hitTargets", data.get("hit_targets", ()))
    if value is None:
        return ()
    if isinstance(value, str):
        return tuple(item.strip() for item in value.split(",") if item.strip())
    if isinstance(value, (bytes, Mapping)) or not isinstance(value, Iterable):
        label = alias or "<missing alias>"
        raise InvalidAliasCatalog(
            f"alias {label} hitTargets must be a list or comma-separated string"
        )

    targets: list[str] = []
    for item in value:
        if not isinstance(item, str):
            label = alias or "<missing alias>"
            raise InvalidAliasCatalog(f"alias {label} hitTargets must contain strings")
        target = item.strip()
        if target:
            targets.append(target)
    return tuple(targets)
