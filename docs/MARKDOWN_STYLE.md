# Markdown Style

Keep documentation concise, scannable, and consistent.

## Headings
- Use sentence case.
- Start at `#` for the document title, then `##`, `###` as needed.
- Keep headings short (3–6 words).

## Lists
- Prefer `-` for bullets.
- One idea per bullet.
- Keep bullet lines short; wrap at ~100 chars.

## Code
- Use fenced code blocks with language where practical.
- Use inline backticks for file paths, CLI flags, and identifiers.

## Links
- Use relative links inside the repo.
- Prefer descriptive link text, not raw URLs.
- When referencing another doc, always link it (avoid bare filenames).
- Example: [docs/FORMAT.md](docs/FORMAT.md), [docs/CLI.md](docs/CLI.md)

## Common docs
- `ARCHITECTURE.md`: system overview and major components.
- `CHANGELOG.md`: user-facing changes by date/version; canonical release notes.
- `CODE_DESIGN.md`: design principles, core abstractions, and key decisions.
- `CODE_STRUCTURE.md`: repo layout and where code and assets live.
- `CONTRIBUTING.md`: how to contribute, dev setup, and workflow.
- `DEVELOPMENT.md`: dev workflows and local setup.
- `FAQ.md`: common questions and short answers.
- `INSTALL.md`: setup steps and prerequisites.
- `NEWS.md`: curated release highlights and announcements; not a full changelog.
- `README.md`: project overview, quick start, and links to key docs.
- `ROADMAP.md`: future plans and non-implemented work.
- `TROUBLESHOOTING.md`: known issues, fixes, and debugging tips.
- `USAGE.md`: how to run the tool, examples, and flags.

## Examples
- Show a minimal example before a complex one.
- Label sample output explicitly if needed.

## Tone
- Write in the present tense.
- Prefer active voice.
- Avoid filler and speculation.
