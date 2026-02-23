# Git & Version Control Standards

## Commit Messages
- **Format:** `<type>: <description>`
- **Length:** Concise, focused
- **No emojis** in commits or PR titles
- **No co-author lines** (no Claude co-author attribution)
- **Types:**
  - `feat:` New feature
  - `fix:` Bug fix
  - `docs:` Documentation only
  - `refactor:` Code restructuring
  - `test:` Adding tests (real tests only)
  - `chore:` Maintenance tasks

## Branch Strategy
- **Feature branches:** `feature/short-description`
- **Bugfix branches:** `fix/issue-description`
- **No spaces** in branch names, use hyphens
- **Delete after merge**

## Commit Practice
- **Atomic commits** - One logical change per commit
- **Test before commit** - Ensure code works
- **No broken commits** - Each commit should work independently
- **Frequent and meaningful** - Track project progress effectively

## Pull Request Process
1. Create feature branch from main
2. Make atomic commits
3. Push branch
4. Create PR with concise description
5. Use `[x]` for completed tasks (not emojis)
6. Reference issues with "Fixes #123"

## .gitignore Notes
- `.context/`, `.rules/`, and `CLAUDE.md` are tracked in this project
- Standard Python ignores apply

---
*Atomic commits, clear messages, clean history.*
