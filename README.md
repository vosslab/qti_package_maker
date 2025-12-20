# QTI Package Maker

`qti_package_maker` is a Python package for generating and converting assessment
packages across LMS formats, including IMS QTI v1.2 and v2.1, Blackboard text
upload, human-readable text, and HTML self-tests.

## Features
- Supports multiple QTI versions (Canvas QTI v1.2 and Blackboard QTI v2.1).
- Handles MC, MA, FIB, NUM, MATCH, ORDER, and MULTI_FIB question types.
- Modular engine system for format-specific readers and writers.
- CLI and Python API workflows.

## Quickstart
Install and usage details live in docs, but the shortest path looks like this:

```sh
pip install qti-package-maker
python3 tools/bbq_converter.py -i bbq-my_questions.txt -f canvas_qti_v1_2
```

For full usage, see [docs/USAGE.md](docs/USAGE.md).

## Standards
- [QTI 2.1 specification (1EdTech)](https://www.1edtech.org/standards/qti/index#QTI21)
- [QTI 1.2 specification (1EdTech)](https://www.1edtech.org/standards/qti/index#QTI%201.2)

## Documentation
- Installation: [docs/INSTALL.md](docs/INSTALL.md)
- Usage and CLI: [docs/USAGE.md](docs/USAGE.md)
- Question types: [docs/QUESTION_TYPES.md](docs/QUESTION_TYPES.md)
- Engines and capabilities: [docs/ENGINES.md](docs/ENGINES.md)
- Formats: [docs/FORMATS.md](docs/FORMATS.md)
- Troubleshooting: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- Developer guide: [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
- Roadmap: [docs/ROADMAP.md](docs/ROADMAP.md)
- Backlog: [docs/TODO.md](docs/TODO.md)
- Changelog: [docs/CHANGELOG.md](docs/CHANGELOG.md)
- Related projects: [docs/RELATED_PROJECTS.md](docs/RELATED_PROJECTS.md)
- Community and support: [docs/COMMUNITY.md](docs/COMMUNITY.md)

## Development
Contributions are welcome. Start with [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
and note changes in [docs/CHANGELOG.md](docs/CHANGELOG.md).

## License
See [LICENSE](LICENSE).

## Acknowledgments
- Based on the IMS Global QTI specification.
- Inspired by the need for cross-platform assessment portability.
- Developed to improve e-learning content interoperability.
- Funding for production from Illinois Library OER grant.
