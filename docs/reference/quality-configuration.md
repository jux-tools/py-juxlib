# Quality Configuration

Single source of truth for all quality settings in py-juxlib.

## Formatting Standards

| Setting | Value | Applies To |
|---------|-------|------------|
| Indent style | spaces | All files |
| Indent size | 4 | Python files |
| Indent size | 2 | YAML, JSON, TOML, Markdown |
| Line length | 88 | Python (ruff default) |
| End of line | lf | All files |
| Final newline | yes | All files |
| Trim trailing whitespace | yes | All files |
| Quote style | double | Python strings |

## Quality Checks by Stage

| Check | Pre-commit | Pre-push | CI | Notes |
|-------|------------|----------|-----|-------|
| Trailing whitespace | Yes | - | Yes | Auto-fix locally |
| End-of-file fixer | Yes | - | Yes | Auto-fix locally |
| YAML/JSON/TOML syntax | Yes | - | Yes | Fast validation |
| Merge conflict markers | Yes | - | Yes | Prevents bad commits |
| Large file check | Yes | - | Yes | Max 1MB |
| Secret detection (gitleaks) | Yes | - | Yes | Critical security |
| Ruff linting | Yes | - | Yes | Auto-fix enabled |
| Ruff formatting | Yes | - | Yes | Auto-fix enabled |
| mypy type checking | - | Yes | Yes | Full strict mode |
| pytest (fast) | - | Yes | Yes | Exclude slow/integration |
| pytest (full) | - | - | Yes | CI only |
| Coverage report | - | - | Yes | CI only, >85% required |

## Tool Versions

| Tool | Min Version | Purpose |
|------|-------------|---------|
| pre-commit | 3.0 | Hook framework |
| ruff | 0.4 | Linting and formatting |
| mypy | 1.10 | Type checking |
| pytest | 8.0 | Testing |
| gitleaks | 8.18 | Secret detection |

## Configuration Files

| File | Tool | Purpose |
|------|------|---------|
| `.editorconfig` | Editors | Formatting baseline |
| `.pre-commit-config.yaml` | pre-commit | Hook definitions |
| `pyproject.toml` | ruff, mypy, pytest | Tool-specific settings |

## Validation Checklist

- [ ] `.editorconfig` matches Formatting Standards table
- [ ] `pyproject.toml` [tool.ruff] line-length = 88
- [ ] `pyproject.toml` [tool.ruff.format] indent-style = "space"
- [ ] `pyproject.toml` [tool.mypy] python_version = "3.11", strict = true
- [ ] Pre-commit runs all "Pre-commit: Yes" checks
- [ ] Pre-push runs all "Pre-push: Yes" checks
- [ ] CI runs all checks marked "CI: Yes"

## Bypassing Hooks (Emergency Only)

```bash
# Skip pre-commit (document reason in commit message)
git commit --no-verify -m "message"

# Skip pre-push
git push --no-verify
```

Always document why hooks were bypassed and create follow-up issue to fix.
