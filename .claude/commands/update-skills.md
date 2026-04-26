---
description: Update skills in target project from my-skills
allowed-tools: Bash, Read
---

# Update Skills

Update existing project's skills from the latest my-skills version.

## Usage

```
/update-skills <target-path> [--options]
```

## Instructions

1. **Parse arguments**:
   - First argument: target project path (required, 除非使用 --all-targets)
   - Options:
     - `--hooks`: Update hooks directory
     - `--settings`: Update settings.json
     - `--ci`: Update CI/CD workflows
     - `--scripts`: Update scripts
     - `--all`: Update everything
     - `-f`, `--force`: Skip confirmation
     - `--dry-run`: Show what would change without making changes
     - `--all-targets`: 同步到 sync-targets.json 中记录的所有目标
     - `--list`: 显示已记录的同步目标

2. **Validate paths**:
   ```bash
   # Get my-skills directory
   MY_SKILLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

   # Validate target exists and has .claude/skills
   TARGET_DIR="$(cd "$TARGET_PATH" 2>/dev/null && pwd)"
   if [ ! -d "$TARGET_DIR/.claude/skills" ]; then
       echo "Error: Target doesn't have .claude/skills. Use /copy-skills for first-time setup."
       exit 1
   fi
   ```

3. **Show changes** (if not --force):
   ```bash
   # Show what skills are new/updated
   echo "Checking for updates..."

   # List skills in source but not in target
   for skill in "$MY_SKILLS_DIR/.claude/skills"/*/; do
       skill_name=$(basename "$skill")
       if [ ! -d "$TARGET_DIR/.claude/skills/$skill_name" ]; then
           echo "  [NEW] $skill_name"
       else
           # Compare modification times or content
           if [ "$skill/SKILL.md" -nt "$TARGET_DIR/.claude/skills/$skill_name/SKILL.md" ]; then
               echo "  [UPDATE] $skill_name"
           fi
       fi
   done
   ```

4. **Update content**:
   ```bash
   # Use rsync or cp to update, preserving existing files
   rsync -av --delete "$MY_SKILLS_DIR/.claude/skills/" "$TARGET_DIR/.claude/skills/"
   rsync -av --delete "$MY_SKILLS_DIR/.claude/agents/" "$TARGET_DIR/.claude/agents/"
   rsync -av --delete "$MY_SKILLS_DIR/.claude/commands/" "$TARGET_DIR/.claude/commands/"
   ```

5. **Handle optional components** based on flags

## Examples

```bash
# Update skills only
/update-skills ~/projects/my-app

# Show what would change without making changes
/update-skills ~/projects/my-app --dry-run

# Update everything
/update-skills ~/projects/my-app --all

# Update without confirmation
/update-skills ~/projects/my-app --all -f
```

## What Gets Updated

| Option | Content |
|--------|---------|
| (default) | `.claude/skills/`, `.claude/agents/`, `.claude/commands/` (sync: new/updated/deleted) |
| `--hooks` | `.claude/hooks/` |
| `--settings` | `.claude/settings.json` |
| `--ci` | `.github/workflows/` |
| `--scripts` | `scripts/*.py`, `scripts/requirements.txt` |
| `--all` | All of the above |

## Copy vs Update

| Command | Use Case | Behavior |
|---------|----------|----------|
| `/copy-skills` | First-time setup | Copies files, doesn't delete |
| `/update-skills` | Sync updates | Syncs changes (adds/updates/deletes) |

## After Updating

The target project will have the latest skills. Changes include:
- New skills added to my-skills
- Updated skill definitions
- Removed skills deleted from target

User should:
```bash
cd ~/projects/my-app
git status  # Review changes
git add .claude/skills/
git commit -m "chore: sync skills from my-skills"
```

## Sync Target Management

同步目标记录在 `.claude/sync-targets.json`。

### 查看已记录的目标
```bash
/update-skills --list
```

### 同步到所有已记录目标
```bash
/update-skills --all-targets
# 等同于依次执行:
# /update-skills /path/to/target1
# /update-skills /path/to/target2
# ...
```

### 同步到所有目标并更新全部内容
```bash
/update-skills --all-targets --all
```

**重要**: 每次执行 update-skills 后，自动更新 `.claude/sync-targets.json` 中对应目标的 last_sync 时间戳。
