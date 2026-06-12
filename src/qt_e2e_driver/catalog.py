from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from .errors import DuplicateAliasError, EmptyAliasCatalog, UnknownAliasInCatalog


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
        hit_targets = data.get("hitTargets", data.get("hit_targets", ()))
        if isinstance(hit_targets, str):
            hit_targets = [item.strip() for item in hit_targets.split(",") if item.strip()]
        return cls(
            alias=alias,
            object_name=object_name,
            page=str(data.get("page", "")),
            owner=str(data.get("owner", "")),
            role=str(data.get("role", "")),
            class_hint=str(data.get("classHint", data.get("class_hint", ""))),
            required=bool(data.get("required", False)),
            deprecated=bool(data.get("deprecated", False)),
            description=str(data.get("description", "")),
            hit_targets=tuple(str(item) for item in hit_targets),
        )


class AliasCatalog:
    def __init__(self, entries: Iterable[AliasEntry]) -> None:
        self._entries: dict[str, AliasEntry] = {}
        for entry in entries:
            if not entry.alias:
                raise EmptyAliasCatalog("alias catalog contains an entry without alias")
            if entry.alias in self._entries:
                raise DuplicateAliasError(f"duplicate alias in catalog: {entry.alias}")
            self._entries[entry.alias] = entry
        if not self._entries:
            raise EmptyAliasCatalog("list-aliases returned an empty alias catalog")

    @classmethod
    def from_payload(cls, payload: Any) -> "AliasCatalog":
        if isinstance(payload, Mapping):
            payload = payload.get("aliases", ())
        return cls(AliasEntry.from_mapping(item) for item in payload)

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
            raise UnknownAliasInCatalog(
                f"UNKNOWN_ALIAS_IN_CATALOG: {alias}; available aliases: {available}"
            ) from exc


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
