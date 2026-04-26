---
description: Create a conventional commit following project standards
allowed-tools: Bash(git:*), Read
---

# Git Commit

Create a conventional commit for the current changes.

## Instructions

1. **Check git status**:
   ```bash
   git status
   ```

2. **Review changes**:
   ```bash
   git diff --stat
   ```

3. **Read workflow standards** (if needed):
   - Read `.claude/agents/github-workflow.md` for commit message format

4. **Analyze the changes** to determine:
   - **Type**: feat, fix, docs, style, refactor, test, chore, perf, ci
   - **Scope**: Which module/area is affected (optional)
   - **Description**: Clear, concise description (use imperative mood)

5. **Stage the changes**:
   ```bash
   git add <files>
   ```

6. **Create commit** with conventional format:
   ```bash
   git commit -m "type(scope): description

   ## Summary
   [Brief explanation of what changed and why]

   ## Breaking Changes
   [List any breaking changes, or omit if none]

   Co-Authored-By: Claude <noreply@anthropic.com>"
   ```

## Commit Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(auth): add login` |
| `fix` | Bug fix | `fix(api): handle timeout` |
| `docs` | Documentation | `docs(readme): update setup` |
| `style` | Formatting | `style: fix indentation` |
| `refactor` | Code change | `refactor: simplify logic` |
| `test` | Test changes | `test: add unit tests` |
| `chore` | Maintenance | `chore(deps): update deps` |
| `perf` | Performance | `perf: optimize queries` |
| `ci` | CI/CD | `ci: add github actions` |

## Examples

```bash
# Feature addition
git commit -m "feat(user): add profile page

Co-Authored-By: Claude <noreply@anthropic.com>"

# Bug fix
git commit -m "fix(login): prevent session hijacking

Co-Authored-By: Claude <noreply@anthropic.com>"

# Documentation
git commit -m "docs(api): update authentication docs

Co-Authored-By: Claude <noreply@anthropic.com>"

# Refactoring
git commit -m "refactor(auth): extract common validation logic

Co-Authored-By: Claude <noreply@anthropic.com>"
```

## After Committing

Verify the commit:
```bash
git log -1 --pretty=fuller
git show --stat
```
