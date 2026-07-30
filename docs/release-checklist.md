# Release Checklist

Use this checklist before tagging any release.

## 1. Branch and scope

- [ ] Only intended release changes are present
- [ ] Changelog/release notes drafted
- [ ] Version metadata updated where needed

## 2. Quality gates

- [ ] CI is green on the release commit
- [ ] Backend checks pass (`python -m compileall enki_ai tests` + `pytest tests/ -v`)
- [ ] Frontend build passes (`npm run build:frontend`)

## 3. Security and data hygiene

- [ ] No secrets or local state files are included
- [ ] Generated artifacts are excluded from commit scope
- [ ] Archive boundaries are respected (`docs/archive/` for non-product material)

## 4. Release execution

- [ ] Merge approved PR into `main`
- [ ] Create annotated tag (`vX.Y.Z`)
- [ ] Publish release notes with key changes and upgrade guidance
