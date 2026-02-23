# Task Completion Checklist

When a task is completed, run through these steps:

## 1. Lint and Format
```bash
ruff check --fix --unsafe-fixes .
ruff format .
```

## 2. Type Check
```bash
mypy src/
```

## 3. Run Tests
```bash
pytest tests/ --cov=markit_mistral --cov-report=term-missing
```

## 4. Review Changes
```bash
git diff
git status
```

## 5. Commit (if appropriate)
- Atomic commits with concise messages
- No emojis, no co-author lines
- Use feature branches for multi-step work

## 6. Update Context (if applicable)
- `.context/plan.md` - Update task status
- `.context/scratch_history.md` - Log any failed attempts
- `.context/research.md` - Document any new findings
