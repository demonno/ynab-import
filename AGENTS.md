# For AI Assistants

Quick guidelines for Claude Code and other AI helping with this project.

## Start Here

1. Read [CLAUDE.md](CLAUDE.md) for architecture and code standards
2. Run `make install && make test` to verify environment
3. Check existing providers in `ynab_import/infra/*/providers.py` for patterns

## Key Rules

**Testing:** All new code needs tests. Test structure mirrors source: `tests/tbc/` ↔ `ynab_import/infra/tbc/`

**Code Quality:** Always run before commit:
- `make fmt` — format code
- `make lint` — check style
- `make check` — verify type hints

**Git:** Commit frequently after each passing test. Format: `type(scope): what` (e.g., `feat(tbc): add reader`)

**No Placeholders:** Don't commit TODO/TBD code. If you can't finish, don't start.

## Important Files

- `CLAUDE.md` — Read this first for context
- `pyproject.toml` — Dependencies and tool configs
- `tests/conftest.py` — Pytest fixtures
- `.pre-commit-config.yaml` — Auto-format hooks

## When to Ask the User

- Architecture decisions (e.g., "Add new bank?")
- Scope changes
- Breaking changes
- Merge strategy

## Example: Add a Bank Provider

1. Create `ynab_import/infra/mybank/models.py` with CSV dataclass
2. Create `ynab_import/infra/mybank/providers.py` with reader (copy pattern from TBC)
3. Write test: `tests/mybank/test_providers.py` (failing first)
4. Implement minimal code to pass test
5. Update README with bank name
6. Commit: `feat(mybank): add MyBank CSV reader`
