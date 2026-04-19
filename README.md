# ynab-import

Automate transaction imports from bank CSV exports to YNAB API.

**Supported banks:** Swedbank, Revolut, TBC

## Install

```bash
pip install ynab-import
```

## Quick Start

```bash
# Configure with your YNAB API credentials
export YNAB_API_KEY=your_token
export YNAB_BUDGET_ID=your_budget_id
export YNAB_ACCOUNT_ID=your_account_id

# Import transactions
ynab-import --config .env import
```

## Development

```bash
make install      # Install dependencies
make test         # Run tests (2 passed, 1 skipped)
make fmt          # Format code
make lint         # Check code quality
make check        # Full checks (lint + type)
```

See [CLAUDE.md](CLAUDE.md) for architecture and [AGENTS.md](AGENTS.md) for AI assistant guidelines.

## Publishing

### Test PyPI (Automatic)
- Every successful master commit auto-publishes to Test PyPI
- Available at: https://test.pypi.org/project/ynab-import/
- Test install: `pip install -i https://test.pypi.org/simple/ ynab-import==0.0.10`

### PyPI (Manual Release)
- Create GitHub release with matching version tag
- Automatically publishes to PyPI
- Requires: `TEST_PYPI_API_KEY` and `PYPI_API_KEY` secrets configured in GitHub

## License

MIT
