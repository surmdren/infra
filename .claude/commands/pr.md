---
description: Create a pull request following project conventions
allowed-tools: Bash(git:*), Bash(gh:*), Read
---

# Create Pull Request

Create a pull request following conventional commit format.

## Instructions

1. **Check current branch**:
   ```bash
   git branch --show-current
   git status
   ```

2. **Push branch to remote** (if not already pushed):
   ```bash
   git push -u origin $(git branch --show-current)
   ```

3. **Analyze changes**:
   ```bash
   # Get commit history for this branch
   git log main..HEAD --oneline

   # Get diff statistics
   git diff main...HEAD --stat

   # Get list of changed files
   git diff main...HEAD --name-only
   ```

4. **Read workflow standards** (if needed):
   - Read `.claude/agents/github-workflow.md` for PR format

5. **Generate PR title** following conventional commit format:
   ```
   type(scope): description
   ```

6. **Generate PR body** with:
   - **Summary**: 1-3 bullet points describing the changes
   - **Changes**: Detailed list of what changed
   - **Test Plan**: Checklist of testing done
   - **Breaking Changes**: Any breaking changes (if applicable)

7. **Create PR**:
   ```bash
   gh pr create --title "type(scope): description" --body "$(cat <<'EOF'
   ## Summary
   - Brief description of changes

   ## Changes
   - [Change 1]
   - [Change 2]

   ## Test Plan
   - [ ] Tests pass locally
   - [ ] Manual testing completed
   - [ ] Documentation updated

   ## Breaking Changes
   [List any breaking changes, or "None"]

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   EOF
   )"
   ```

8. **Verify PR was created**:
   ```bash
   gh pr view
   ```

## PR Title Examples

| Type | Example |
|------|---------|
| Feature | `feat(auth): add OAuth2 login` |
| Bug Fix | `fix(api): resolve timeout issue` |
| Docs | `docs(readme): update installation guide` |
| Refactor | `refactor(components): simplify state management` |
| Test | `test(integration): add E2E tests` |
| Chore | `chore(deps): upgrade to Node.js 20` |

## PR Body Template

```markdown
## Summary
- [Change 1]
- [Change 2]
- [Change 3]

## Changes
### Feature/Module 1
- [Detail 1]
- [Detail 2]

### Feature/Module 2
- [Detail 1]
- [Detail 2]

## Test Plan
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] No regressions detected

## Breaking Changes
- [List breaking changes, or "None"]

## Screenshots
[Add screenshots if applicable]

## Related Issues
Closes #ISSUE_NUMBER
Related to #ISSUE_NUMBER

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

## Checklist

Before creating PR, ensure:
- [ ] Branch name follows convention (`type/description`)
- [ ] At least one commit with conventional format
- [ ] PR title follows conventional format
- [ ] PR description is complete
- [ ] Tests pass locally
- [ ] No lint errors
- [ ] Changes are focused on a single concern
