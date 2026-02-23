# CI/CD Workflow Standards

## Existing Workflows
- `ci.yml` - Lint and test on push/PR (Python matrix: 3.10-3.13)
- `pages.yml` - Deploy docs to GitHub Pages
- `publish.yml` - Publish package to PyPI on release

## Key Practices
- **Pin versions:** `actions/checkout@v4` (reproducibility)
- **Cache deps:** Speed matters for developer happiness
- **Fail fast:** Lint -> Test -> Build -> Deploy
- **Matrix testing:** Test all supported Python versions (3.10-3.13)
- **Secrets:** Never commit credentials (MISTRAL_API_KEY via env vars)

## Local CI Testing
- `act` is available for running GitHub Actions locally
- Note: Some environments may not run correctly on macOS

---
*Fast feedback, high confidence, zero surprises.*
