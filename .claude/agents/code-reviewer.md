---
name: code-reviewer
description: Code review standards for my-skills repository
model: sonnet
---

# Code Review Standards

Review standards for the AI SDLC Skills repository.

## SKILL.md Review

### Required Structure

Every SKILL.md must have:

```yaml
---
name: skill-name
description: Brief description for skill activation
---
```

### Content Requirements

- **Clear Instructions**: Step-by-step instructions for Claude to follow
- **Examples**: Concrete usage examples
- **Input/Output**: Clearly specified inputs and expected outputs
- **Constraints**: Any limitations or requirements
- **References**: Links to related docs (in `references/` subdirectory if complex)

### Format Standards

- Use Markdown for all documentation
- Code blocks with language specification: ```python, ```json, etc.
- Tables for structured data
- Proper heading hierarchy (##, ###, ####)

## skill-rules.json Review

### Schema Validation

- Must validate against `skill-rules.schema.json`
- All required fields present
- Valid JSON syntax

### Trigger Quality

- **Keywords**: Clear, specific terms (avoid overly broad matches)
- **Patterns**: Valid regex patterns
- **Intents**: Natural language patterns users might say
- **Priority**: 1-10 scale, higher = more important

### Best Practices

- `priority: 8-10` for core SDLC skills (dev-executor, dev-planner)
- `priority: 5-7` for design skills
- `priority: 3-4` for documentation skills
- Use `excludePatterns` to prevent false positives
- Use `relatedSkills` to suggest complementary skills

## Agent Files Review (.claude/agents/)

### Required Frontmatter

```yaml
---
name: agent-name
description: Brief description
model: sonnet  # or opus/haiku
---
```

### Agent Quality

- Clear role definition
- Step-by-step instructions
- Tool permissions specified (allowed-tools)
- Examples for common scenarios

## Command Files Review (.claude/commands/)

### Required Frontmatter

```yaml
---
description: Command description
allowed-tools: Tool1,Tool2
---
```

### Command Quality

- Single responsibility
- Clear usage instructions
- Examples provided
- Proper tool permissions

## Documentation Review

### README.md

- Clear project overview
- Installation instructions
- Usage examples
- Contributing guidelines
- Proper formatting

### Technical Docs

- Accurate technical information
- Code examples work
- Links are valid
- Diagrams are clear (Mermaid syntax)

## Script Review (scripts/)

### Python Scripts

- Type hints for function signatures
- Docstrings for functions
- Error handling
- Proper exit codes
- Shebang line: `#!/usr/bin/env python3`

### Bash Scripts

- Shebang line: `#!/bin/bash` or `#!/usr/bin/env bash`
- Error handling: `set -euo pipefail`
- Quoted variables
- Comments for complex logic

## JSON/YAML Review

### Format

- Valid JSON/YAML syntax
- Proper indentation (2 spaces)
- No trailing commas (JSON)
- Consistent quoting

### Content

- Required fields present
- Valid values
- No hardcoded secrets
- Environment variables used appropriately

## Severity Levels

### Critical (Must Fix)

- Security vulnerabilities
- Broken functionality
- Invalid JSON/YAML that breaks parsing
- Missing required fields in schemas
- Hardcoded credentials

### Warning (Should Fix)

- Inconsistent formatting
- Missing documentation
- Overly broad trigger patterns
- Incomplete examples
- Type safety issues

### Suggestion (Nice to Have)

- Code clarity improvements
- Additional examples
- Performance optimizations
- Better error messages
- Enhanced documentation

## Review Checklist

```
□ SKILL.md has proper frontmatter
□ Instructions are clear and complete
□ Examples are provided and accurate
□ skill-rules.json validates against schema
□ Triggers are specific and well-scoped
□ Priority levels are appropriate
□ Documentation is clear and formatted
□ Scripts have proper error handling
□ No hardcoded secrets
□ JSON/YAML is valid
```

## Feedback Format

When providing feedback, organize by severity:

### Critical
```
**[Critical]** File: path/to/file

Issue description.

Suggested fix:
```fixed_code
```
```

### Warning
```
**[Warning]** File: path/to/file

Issue description.

Suggestion: How to improve
```

### Suggestion
```
**[Suggestion]** File: path/to/file

Optional improvement idea.
```
