# Contributing Guide

This document outlines our development workflow, branch naming conventions, and collaboration practices.

## Branch Naming Conventions

All branches must follow this pattern:

```
<name>/<type>/DAT-XX-<short-description>
```

- `name` is your first name (lowercase)
- `type` is one of the branch types below
- `DAT-XX` is the Linear issue ID
- `short-description` is a few words separated by hyphens

### Branch Types

| Prefix | Purpose | Example |
|--------|---------|---------|
| `explore/` | Data exploration, notebook analysis | `naman/explore/DAT-42-audit-log` |
| `feat/` | New features, scripts, pipelines | `ishaan/feat/DAT-56-load-data` |
| `fix/` | Bug fixes | `river/fix/DAT-55-null-timestamp` |
| `hotfix/` | Urgent production fixes | `naman/hotfix/DAT-60-query-crash` |
| `chore/` | Maintenance, dependencies, setup | `naman/chore/DAT-30-team-onboarding-setup` |
| `docs/` | Documentation only | `river/docs/DAT-49-auth-log-findings` |
| `refactor/` | Code restructure (no behavior change) | `naman/refactor/DAT-90-clean-parsers` |
| `test/` | Adding or updating tests | `ishaan/test/DAT-100-add-unit-tests` |
| `ci/` | CI/CD pipeline changes | `naman/ci/DAT-110-add-lint-step` |

### Examples

```bash
# Creating an exploration branch for notebook analysis
git checkout dev
git pull origin dev
git checkout -b naman/explore/DAT-48-labels-jsonl

# Creating a docs branch for a findings doc
git checkout dev
git pull origin dev
git checkout -b river/docs/DAT-49-auth-log-findings

# Creating a feature branch
git checkout dev
git pull origin dev
git checkout -b ishaan/feat/DAT-56-load-data
```

## Git Workflow

We use a **trunk-based development** approach with two main branches:

```
main (production)
  └── dev (integration)
        └── feat/*, fix/*, etc. (short-lived feature branches)
```

### Workflow Steps

1. **Create a Linear issue** for your work
2. **Create a branch** from `dev` using the naming convention
3. **Make your changes** with meaningful commits
4. **Push and create a PR** to `dev`
5. **Request review** from at least one team member
6. **Address feedback** and get approval
7. **Merge to dev** (squash merge preferred)
8. **PR from dev to main** for releases

### Commit Messages

Use clear, descriptive commit messages:

```
feat(parser): add DNS log parser with exfiltration detection

- Implement regex patterns for DNS query parsing
- Add detection logic for unusually long subdomains
- Include unit tests for common log formats

Closes DAT-42
```

Format: `<type>(<scope>): <description>`

## Pull Request Guidelines

### Before Creating a PR

- [ ] Code follows project style guidelines
- [ ] All tests pass locally (`pytest`)
- [ ] Linting passes (`ruff check .`)
- [ ] Migrations are valid (`alembic -c alembic/alembic.ini check`)
- [ ] Documentation is updated if needed

### PR Template

```markdown
## Summary
Brief description of changes

## Linear Issue
DAT-XXX

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Documentation
- [ ] Refactoring
- [ ] CI/CD

## Testing
- [ ] Unit tests added/updated
- [ ] Manual testing completed

## Screenshots (if applicable)
```

### Review Process

1. At least **1 approval** required for dev merges
2. All **CI checks must pass**
3. **No unresolved conversations**
4. Reviewer should test locally if significant changes

## Database Migrations

### Creating a Migration

```bash
# Ensure your models are updated in src/models/
alembic -c alembic/alembic.ini revision --autogenerate -m "descriptive_name"

# Review the generated migration file!
# Then apply locally
APP_ENV=dev alembic -c alembic/alembic.ini upgrade head
```

### Migration Best Practices

- Always review auto-generated migrations
- Test both upgrade AND downgrade
- Keep migrations small and focused
- Never modify a migration that's been merged to dev/main

## Code Style

### Python

- Use `ruff` for linting and formatting
- Type hints required for function signatures
- Docstrings for public functions

```python
def parse_dns_log(line: str) -> dict[str, Any] | None:
    """
    Parse a single DNS log line into structured data.
    
    Args:
        line: Raw log line from dnsmasq
        
    Returns:
        Parsed log data or None if parsing fails
    """
    ...
```

### SQL

- Use UPPERCASE for SQL keywords
- Use snake_case for table and column names
- Always specify column names in INSERT statements

```sql
SELECT 
    h.hostname,
    COUNT(e.event_id) AS event_count
FROM hosts h
JOIN log_events e ON h.host_id = e.host_id
WHERE e.event_time >= '2024-01-01'
GROUP BY h.hostname
ORDER BY event_count DESC;
```

## Local Development

### Starting Fresh

```bash
# Reset database
docker-compose down -v
docker-compose up -d
alembic -c alembic/alembic.ini upgrade head
```

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_parsers.py

# With coverage
pytest --cov=src
```

### Checking Code Quality

```bash
# Lint
ruff check .

# Format
ruff format .

# Type check (if using mypy)
mypy src/
```

## CI/CD Pipeline

### What GitHub Actions does

CI runs automatically on **pull requests to `dev`** and on **pushes to `dev`** (after merge):

- Ruff lint and format checks
- Alembic migrations validated against an **ephemeral CI test database** (a Postgres container that lives and dies inside the GitHub Actions runner)
- Unit tests run against the same test database
- No real developer database is touched -- GitHub Actions has no access to your local Postgres

### After merge to `dev` -- local steps

Our databases are local-only (Docker on each teammate's machine). GitHub Actions cannot update them. After a PR is merged to `dev`, every teammate should run:

```bash
git checkout dev
git pull origin dev
alembic -c alembic/alembic.ini upgrade head
```

If migrations added new tables or columns and you want data populated:

```bash
# Run the relevant loader(s) for your local database
# (loader scripts and instructions vary by table -- check the PR or ask in Slack)
```

### Deploy workflows (deferred)

`deploy-dev.yml` and `deploy-prod.yml` exist but are **disabled** (`workflow_dispatch` only, no automatic triggers). They are placeholders for when/if the team sets up a cloud-hosted database or a self-hosted GitHub Actions runner. They will not run on any merge or push.

### Branch protection

- Direct pushes to `dev` are blocked; all changes go through pull requests
- The `Test` status check must pass before merge
- At least 1 approving review is required

## Questions?

- Check existing Linear issues
- Ask in #data201-project Slack channel
- Tag teammates in relevant Linear issues
