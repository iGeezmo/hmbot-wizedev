# Repository instructions

## AI digest mirror

- `docs/ai-digest.md` is a generated mirror index. Do not edit it by hand for a new daily issue.
- Add each new issue as `docs/ai-digest-entries/YYYY-MM-DD.md`.
- The entry must start with exactly `## YYYY-MM-DD` and must not contain frontmatter.
- Do not create a duplicate date.
- Include only the general public digest. Never copy project-specific scouting, private repository details, credentials, internal URLs, or personal data into this public repository.
- `.github/workflows/render-ai-digest.yml` rebuilds the accumulated document after an entry is added.
- The canonical private source and mirror targets are registered in `iGeezmo/0dai/docs/ai-digest-mirrors.json`.
