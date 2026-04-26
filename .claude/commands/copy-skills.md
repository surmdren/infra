---
description: Copy my-skills to another project directory
allowed-tools: Bash, Read
---

# Copy Skills

Copy my-skills configuration to another project for reuse.

## Usage

```
/copy-skills <target-path> [--options]
```

## Instructions

1. **Parse arguments**:
   - First argument: target project path (required)
   - Options:
     - `--hooks`: Copy hooks directory
     - `--settings`: Copy settings.json
     - `--ci`: Copy CI/CD workflows
     - `--scripts`: Copy Python scripts
     - `--all`: Copy everything
     - `-f`, `--force`: Skip confirmation

2. **Validate paths**:
   ```bash
   # Get my-skills directory
   MY_SKILLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

   # Validate target exists
   TARGET_DIR="$(cd "$TARGET_PATH" 2>/dev/null && pwd)"
   ```

3. **Copy content** based on options:
   - **skills** (always copied): `.claude/skills/` → `$TARGET/.claude/skills/`
   - **agents** (always copied): `.claude/agents/` → `$TARGET/.claude/agents/`
   - **commands** (always copied): `.claude/commands/` → `$TARGET/.claude/commands/`
   - **hooks** (if --hooks): `.claude/hooks/` → `$TARGET/.claude/hooks/`
   - **settings** (if --settings): `.claude/settings.json` → `$TARGET/.claude/settings.json`
   - **ci** (if --ci): `.github/workflows/` → `$TARGET/.github/workflows/`
   - **scripts** (if --scripts): `scripts/*.py` → `$TARGET/scripts/`

4. **Execute copy commands**:
   ```bash
   # Always copy skills, agents, commands
   mkdir -p "$TARGET_DIR/.claude"
   cp -r "$MY_SKILLS_DIR/.claude/skills" "$TARGET_DIR/.claude/"
   cp -r "$MY_SKILLS_DIR/.claude/agents" "$TARGET_DIR/.claude/"
   cp -r "$MY_SKILLS_DIR/.claude/commands" "$TARGET_DIR/.claude/"

   # Optional components based on flags
   ```

## Examples

```bash
# Copy only skills (minimal)
/copy-skills ~/projects/my-app

# Copy skills + hooks
/copy-skills ~/projects/my-app --hooks

# Copy everything
/copy-skills ~/projects/my-app --all

# Copy without confirmation
/copy-skills ~/projects/my-app --all -f
```

## What Gets Copied

| Option | Content |
|--------|---------|
| (default) | `.claude/skills/`, `.claude/agents/`, `.claude/commands/` |
| `--hooks` | `.claude/hooks/` |
| `--settings` | `.claude/settings.json` |
| `--ci` | `.github/workflows/` |
| `--scripts` | `scripts/*.py`, `scripts/requirements.txt` |
| `--all` | All of the above |

## Sync Target Management

同步目标记录在 `.claude/sync-targets.json`，每次复制后自动更新。

### 查看已记录的目标
```bash
/copy-skills --list
# 或查看文件
cat .claude/sync-targets.json
```

### 同步到所有已记录目标
```bash
/update-skills --all-targets
```

### sync-targets.json 格式
```json
{
  "targets": [
    {
      "path": "/path/to/project",
      "alias": "project-name",
      "last_sync": "2025-01-25T12:00:00",
      "sync_type": "copy-skills --all"
    }
  ]
}
```

**重要**: 每次执行 copy-skills 后，自动更新 `.claude/sync-targets.json`：
1. 如果目标路径已存在，更新 last_sync 和 sync_type
2. 如果是新目标，添加到 targets 列表

## After Copying

The target project will have my-skills available. User can:
```bash
cd ~/projects/my-app
claude-code
# Then use skills like /requirement-detail, /tech-solution, etc.
```
