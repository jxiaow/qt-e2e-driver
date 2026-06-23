# AI Integration Kit

## Goal

Keep AI-facing integration docs and tools practical, verifiable, and aligned with the JSON alias catalog direction.

## Repo Facts

- Scanner CLI lives in `src/qt_e2e_driver/scanner.py`.
- Doctor CLI lives in `src/qt_e2e_driver/doctor.py`.
- Console scripts are declared in `pyproject.toml`.
- AI-facing implemented docs live in `docs/AI_INTEGRATION_PLAYBOOK.md`.
- Future integration work lives in `harness/project/operations/ai-integration-kit/`.
- Build recipes live in `docs/recipes/`.
- The preferred alias source of truth is `tests/e2e/aliases.json` in product repositories.

## Core Rules

- AI guidance should favor JSON alias catalogs over long hand-written C++ registry blocks.
- Scanner output may suggest aliases, but suggestions are drafts and must be reviewed.
- Doctor output should be deterministic enough for an AI to run, patch, and rerun.
- Build-system-specific behavior belongs in recipes; shared code should stay build-system-neutral.
- Do not promise fully automatic product patching unless the implementation exists.

## Design Checklist

- Is this instruction for humans, AI agents, or both?
- Can the agent verify the instruction with a command?
- Does the guidance work for qmake, CMake, and Visual Studio projects?
- Does it preserve production/test separation?

## Implementation Checklist

- Add docs or operations tests for new mandatory playbook or backlog sections.
- Add CLI tests for new scanner or doctor behavior.
- Update README links when adding a new top-level integration document.
- Run full `python -m pytest`.

## Common Smells

- A playbook step says "just register aliases in code" without mentioning JSON catalog or test-only gates.
- Doctor checks only look for text markers and cannot guide repair.
- Scanner silently treats object names as final business aliases.
- Recipes diverge on required adapter source files.
