# Code Review Standards

## PR Review Toolkit
When the `pr-review-toolkit` plugin is available, use it after creating PRs.

### Available Agents
- `code-reviewer` - Review for style, best practices, project guidelines
- `silent-failure-hunter` - Find inadequate error handling, silent failures
- `code-simplifier` - Simplify code while preserving functionality
- `comment-analyzer` - Check comment accuracy and maintainability
- `pr-test-analyzer` - Review test coverage quality
- `type-design-analyzer` - Analyze type design and invariants

### Workflow
1. Create PR with `gh pr create`
2. Run code review agent on the changes
3. Address critical findings before requesting human review

## Manual Code Review Checklist

### Before Committing
- [ ] Code runs without warnings
- [ ] Tests pass
- [ ] No debug code left
- [ ] No sensitive data in code or logs

### Logic & Safety
- [ ] Error cases handled appropriately
- [ ] No silent failures (empty catch blocks)
- [ ] Resource cleanup (files, connections, API clients)

### Code Quality
- [ ] Functions do one thing
- [ ] Clear naming (no abbreviations)
- [ ] No magic numbers (use constants)
- [ ] Comments explain "why", not "what"

---
*Review early, review often, catch issues before they ship.*
