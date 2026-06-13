# Alias Registry

The Qt application is the single source of truth for aliases. Python never stores an `alias -> objectName` copy.

## Entry Fields

| Field | Meaning |
| --- | --- |
| `alias` | Stable test-facing name, such as `login.account`. |
| `page` | Page or business scene used for grouping and diagnostics. |
| `owner` | Maintenance owner, usually the page or module name. |
| `objectName` | Real Qt widget name. |
| `classHint` | Expected widget class for diagnostics. |
| `role` | `input`, `button`, `label`, `container`, or `hitTarget`. |
| `hitTargets` | Named click targets inside a custom-painted widget. |
| `required` | Whether smoke tests must be able to resolve this alias. |
| `deprecated` | Whether the alias is kept only for migration. |
| `description` | Human-readable explanation for test failure output. |

`required` and `deprecated` should be JSON booleans. Python also accepts common string forms such as `true`, `false`, `1`, and `0` to keep hand-authored catalogs easy to debug. Unknown boolean strings fail as malformed catalog data.

`hitTargets` may be a JSON string list or a comma-separated string. Other shapes fail before `UiAliases` is built.

## Naming

Use `page.element` for simple pages:

```text
login.account
login.password
login.submit
login.error
```

Use `domain.page.region.hitTarget` when a page has repeated controls or custom-painted regions:

```text
meeting.mainToolbar.mic
meeting.floatToolbar.mic
meeting.participantList.muteAll
```

`hitTarget` means "the internal area to click inside a QWidget". It does not mean calling a business method.

Multiple hit target aliases may share the same `objectName` when they represent different clickable regions inside one custom-painted QWidget. Ordinary widget aliases should still keep a one-alias-to-one-`objectName` mapping so failures stay easy to diagnose.

## Maintenance Rules

| Change | Update | Do not |
| --- | --- | --- |
| Qt `objectName` renamed | Change registry mapping only. | Rename Python aliases. |
| New testable control | Add `objectName`, registry entry, and query coverage. | Use raw objectName in Python. |
| Control split into child widgets | Point alias to the real interactive child. | Keep clicking the parent center. |
| Custom-painted hit region moved | Update the hit resolver. | Put pixel coordinates in Python. |
| Alias semantics removed | Mark deprecated, migrate tests, then remove. | Reuse old alias for a new meaning. |

## Startup Contract

The test session must call `list-aliases` first. If it cannot load the catalog, tests fail before UI actions run. This keeps failures near the real cause instead of surfacing later as a misleading click or text error.

Python rejects malformed catalog payloads before building `UiAliases`. The response data must contain an `aliases` list, each entry must be an object, every alias entry must include both `alias` and `objectName`, boolean fields must be parseable, and `hitTargets` must contain strings.

`UiAliases` supports lightweight discovery: `dir(ui)` lists top-level alias groups and `dir(ui.login)` lists the next segment below `login`. Unknown aliases include close-match suggestions to catch common typos during test authoring.
