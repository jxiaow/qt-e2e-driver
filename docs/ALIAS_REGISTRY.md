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
