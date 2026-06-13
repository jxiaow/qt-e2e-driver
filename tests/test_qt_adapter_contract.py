from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_alias_registry_validate_has_hit_target_object_name_sharing_rule() -> None:
    source = (ROOT / "src" / "qt" / "AliasRegistry.cpp").read_text(encoding="utf-8")

    assert "canShareObjectName" in source
    assert "hitTargets.isEmpty()" in source
    assert "share objectName" in source
