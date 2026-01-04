# Changelog

## 2026-01-03

### Added
- Add `COLOR_WHEEL_REFACTOR_PLAN.md` with a perceptual color sampling plan and visual test notes.
- Add `qti_package_maker/common/color_wheel_next_gen.py` for OKLCH-based color wheel experiments.
- Add pytest coverage for next-gen color wheel utilities.

### Changed
- Refine `COLOR_WHEEL_REFACTOR_PLAN.md` with perceptual hue spacing and fixed lightness bands.
- Fix `COLOR_WHEEL_REFACTOR_PLAN.md` to use fixed lightness per category instead of random ranges.
- Update `color_wheel_next_gen.py` to support uniform-chroma mode for even hue consistency.
- Adjust `COLOR_WHEEL_REFACTOR_PLAN.md` to define even chroma via shared minimum max chroma.
- Adjust next-gen lightness targets: add `very_dark`, lighten `dark` and `light`, keep `extra_light` stable.
- Optimize next-gen hue offset selection to maximize shared chroma for dark/light categories.
- Anchor next-gen hue 1 at true red via a configurable `anchor_hue`.
- Increase next-gen saturation by blending uniform and per-hue max chroma.
- Compute true-red anchor from sRGB and use a gamma-blended chroma boost to raise saturation.
- Add working history section to `COLOR_WHEEL_REFACTOR_PLAN.md` covering challenges and attempts.
- Add yellow hue balancing to boost dark yellows and reduce light-yellow dominance.
- Document current next-gen tuning values in `COLOR_WHEEL_REFACTOR_PLAN.md`.
- Update `COLOR_WHEEL_REFACTOR_PLAN.md` with design corrections and per-wheel policy guidance.
- Add xdark/normal modes and WheelSpec policy draft to `COLOR_WHEEL_REFACTOR_PLAN.md`.
- Remove xdark/normal from the current WheelSpec draft per updated scope.
- Replace `COLOR_WHEEL_REFACTOR_PLAN.md` with CAM16-based plan and updated rollout steps.
- Update `COLOR_WHEEL_REFACTOR_PLAN.md` to make CAM16 the default (no flags).
- Add CAM16 dependency choice notes and caching detail to `COLOR_WHEEL_REFACTOR_PLAN.md`.
- Move color wheel modules into `qti_package_maker/common/color_wheel/` and add shims for compatibility.
- Expand `color_wheel_next_gen` shim exports to include internal helpers used by tests.
- Remove OKLCH next-gen module and tests; keep legacy wheel in `color_wheel/legacy_color_wheel.py`.
- Add deprecation warning on `qti_package_maker.common.color_wheel` package import.
- Update color wheel tests to import legacy module directly, avoiding deprecation warnings.
- Select `colour-science` as the CAM16 dependency and add it to `pip_requirements.txt`.
- Move color wheel implementations to `qti_package_maker/common/color_theory/` with a legacy facade in `qti_package_maker/common/color_wheel.py`.
- Replace OKLCH next_gen code with CAM16 scaffolding in `qti_package_maker/common/color_theory/next_gen.py`.
- Add `generate_color_wheel` facade with backend selection to `qti_package_maker/common/color_wheel.py`.
- Add facade regression test for legacy backend parity.
- Add CAM16 backend smoke test (requires colour-science).
- Boost CAM16 dark mode saturation and soften light modes for pastel output.
- Add CAM16 spec helper in `next_gen.py` and test J/M/Q ranges in pytest.
- Add a Remaining Items section to `docs/COLOR_WHEEL_REFACTOR_PLAN.md`.
- Add CAM16 debug HTML output with per-swatch J/M/Q values.
- Anchor CAM16 debug output to best-red offsets per mode.
- Make CAM16 debug output deterministic (no M variation) and force hue 1 to max M.
- Add XKCD color name labels to CAM16 debug HTML.
- Stabilize red scan scoring to avoid blowups when R is zero.
- Add CAM16-UCS radius, gamut margin, and per-hue max-M utilization to CAM16 debug HTML.
- Adjust CAM16 target J values for dark/light and update cached light best-red offset.
- Split CAM16 next-gen logic into focused modules (cam16_utils, generator, red_scan, html_tables, specs, utils).
- Add `wheel_specs.yaml` for CAM16 mode parameters with defaults loaded in `wheel_specs.py`.
- Update cached best-red offsets for dark and light modes after retuning J targets.
- Add optional UCS radius targets for light/xlight modes to lift pastel colorfulness.
- Adjust CAM16 target J values for xdark, normal, and light; remove M and gamut_limit from debug table.
- Rotate CAM16 wheels so hue 1 starts at the true red anchor.
- Emit legacy red RGB distance summary in CAM16 HTML output.
- Wire CAM16 adapter and wheel generation skeleton in `qti_package_maker/common/color_theory/next_gen.py`.
- Adjust CAM16 plan to keep CAM16 opt-in until the default is intentionally flipped.
- Use American spelling everywhere except for the `colour-science` package name.
- Add `rgb_color_name_match` helpers for closest xkcd color name matching via seaborn.
- Add `seaborn` to `pip_requirements.txt` for xkcd color lookups.
- Remove `webcolors` dependency now that xkcd names are used.
- Remove `rcp-color-utils.py` scratch module from `qti_package_maker/common/color_theory/`.
- Add pytest coverage for `rgb_color_name_match`.
- Refine CAM16 anchor selection to scan offsets and pick the closest RGB match to the anchor.
- Adjust CAM16 anchor selection to prefer lower green/blue for hue 1 (truer red).
- Anchor selection now evaluates the reddest achievable hue at max chroma for the mode.
- Anchor selection now scans all 360 hue offsets to find the minimal green/blue red.
- Add multi-stage best-red offset search and cache for hue 1 anchoring.
- Seed best-red cache with dark/16 offset 29.9 for the true red anchor.
- Seed best-red cache with updated xdark/dark/normal/light/xlight offsets for 16 colors.
- Add xdark/normal specs for best-red calculations without changing default table modes.
- Expand --best-red to report xdark/dark/normal/light/xlight (or "all").
- Add --red-scan HTML output for 5-degree and 1-degree red offset inspection.
- Refine red_scan.html to show coarse/fine/micro narrowing for true red selection.
- Update red scoring to use G/B balance and R/(G+B) ratio.
- Rotate CAM16 wheels by redness score when anchoring to true red.
- Adjust micro-step size for red scan to 0.2 degrees.
- Switch red scoring to minimize (G+B)/R and |G-B|/(G+B).
- Switch red scoring to minimize |G-B|/(G+B) and (G+B)/(2R).
- Use summed red score (|G-B|/(G+B) + (G+B)/(2R)) for ranking.
- Deduplicate micro-step offsets in red scan output.
- Quantize micro-step offsets to the 0.2 grid for red scan output.
- Generate micro offsets using (base + i * micro_step) % 360.
- Bundle red scan output for all modes into a single HTML file when using --best-red.
- Render red scan bundles in-memory without per-mode temp files.
- Switch next-gen CLI to named args (no positional args).
- Remove --scan-mode now that red scan bundles all modes by default.
- Add pytest coverage for CAM16 next-gen helpers and red scan HTML.
- Force hue 1 for all modes to use max chroma in the HTML table to match the chosen offset.
- Switch next-gen CLI to argparse and make --best-red also write red_scan.html.
- Update TODO to reflect completed BBQ reads and current unimplemented engine items.
- Mark Canvas QTI 1.2 ORDER as won't implement.
- Move module-level asserts into pytest unit coverage.
- Clarify engine prefix selection fix recommendation in modularity report.
- Expand pytest coverage for writers, manifest helpers, base engine helpers, and package interface.
- Expand TODO with actionable fixups, extraction checks, reliability tasks, tests, and docs follow-ups.
- Expand ROADMAP with near-, mid-, long-term priorities and out-of-scope items.
- Add round-trip pytest coverage for BBQ, text2qti, and okla_chrst_bqgen.
- Restore legacy TODO and ROADMAP content to preserve prior planning details.
- Add multi-engine round-trip pytest coverage across BBQ, text2qti, and okla_chrst_bqgen.
- Fix engine selection ambiguity, item bank merge type tracking, and BBQ NUM zero-division handling with tests.
- Expand ROADMAP priorities with additional near-, mid-, and long-term items and out-of-scope notes.
- Add pytest coverage for QTI writer ZIP layout and manifest references.
- Add reader error-path tests and strengthen QTI writer XML assertions.
- Add pytest coverage for xml formatter utilities.
- Expand pytest coverage for validator CRC checks, yaml tools, tabulate compat, string helpers, and color wheel.

## 2025-12-29

### Added
- Add [docs/TEST_PLAN.md](TEST_PLAN.md) with pytest suite ideas before implementation.
- Add pytest unit and integration coverage for item types, validators, engines, and CLI.
- Add pytest fixtures in `tests/conftest.py` for shared sample items and temp cwd.
- Add integration output checks for QTI ZIPs, human readable, BBQ, and HTML outputs.
- Add pytest unit coverage for text2qti and okla_chrst_bqgen reader parsing.
- Add reader/writer roundtrip smoke tests for BBQ, text2qti, and okla_chrst_bqgen engines.
- Add edge-case tests for text2qti and BBQ reader error paths plus okla unknown-block handling.
- Add unit coverage for missing NUM tolerances in BBQ/text2qti readers.
- Add unit coverage for NUM writers with zero tolerance.
- Add unit coverage for engine registry, manifest generation, YAML helpers, and anti-cheat.
- Add [docs/ENGINE_AUTHORING.md](ENGINE_AUTHORING.md) with engine authoring guidance.
- Add internal engine cleanup notes in `qti_package_maker/engines/ENGINE_CLEANUP.txt`.
- Add docs consistency check to keep engine names in sync with the registry.
- Add unit coverage for BaseEngine filename helpers and histogram output.
- Add CLI error-path coverage for invalid BBQ filenames.
- Add manifest schema metadata checks for QTI v1.2 and v2.1 outputs.
- Add engine class contract smoke tests (imports and write_item wiring).
- Add ZIP safety checks to prevent absolute or parent directory paths.
- Add BBQ parsing error-path coverage for missing correct flags.
- Add BaseItem repr smoke test.

### Changed
- Convert script-based tests into pytest functions using fixtures and tmp paths.
- Register pytest `smoke` marker and fix item type test inputs.
- Add format_html_lxml and anti-cheat edge case tests.
- Adjust BaseEngine test harness and anti-cheat expectations for current behavior.
- Use ItemBank.add_item_cls for okla_chrst_bqgen reader to preserve question text.
- Default BBQ NUM tolerance to 0.0 with a warning when the field is missing.
- Fix text2qti MA detection for `[ ]` choices and raise clearer errors for missing NUM/FIB answers.
- Emit explicit tolerance in text2qti NUM writer output (including 0.0).
- Limit BBQ and text2qti read skipping to parse-time ValueError/IndexError.
- Refine engine authoring guidance with overview, discovery command, and ZIP tip.
- Expand engine authoring guidance with examples, mapping table, and troubleshooting.
- Add engine authoring tables for interfaces, artifacts, tests, and failure modes.
- Align engine authoring examples with EngineClass patterns and testing guidance.
- Clarify recommended pytest targets and what they cover for engine authors.
- Rewrite engine docstrings for accuracy and consistency across engine modules.
- Note MkDocs Material light/dark theming for html_selftest in TODO and roadmap.
- Reference MkDocs Material palette tokens in html_selftest theming docs.
- Record engine cleanup completion notes for randomness helper and allow_mixed plumbing.
- Rename random item helper in BaseEngine and update tests.
- Add scoped html_selftest theme injection and palette-aware colors for matching/ordering.
- Document CRC-suffixed JavaScript function naming in html_selftest helpers.
- Use html_selftest theme variables for dropzone borders and reset colors.
- Mark html_selftest MkDocs palette theming as done in TODO/ROADMAP.
- Add html_selftest output validation tests for HTML parsing and theme markers.
- Add html_selftest HTML validator that tolerates JavaScript blocks.
- Update engine docs for html_selftest FIB support and remove stale TODO entry.

## 2025-12-20

### Added
- Add `docs/DEVELOPMENT.md` with setup, testing, and engine guidance.
- Add `docs/FORMATS.md` with input/output format notes and engine list.
- Add `docs/TROUBLESHOOTING.md` with common issues and fixes.
- Add `docs/INSTALL.md`, `docs/USAGE.md`, `docs/QUESTION_TYPES.md`, and
  `docs/ENGINES.md` to split README content into focused guides.
- Add `docs/RELATED_PROJECTS.md` and `docs/COMMUNITY.md` to move link lists and
  support info out of README.
- Add `TODO.md` to track feature ideas and missing item implementations, migrated from
  `TODO.txt`.
- Add `ROADMAP.md` to capture longer-form plans such as hints support.
- Add feedback planning section to `ROADMAP.md`.

### Changed
- Update `README.md` with documentation links and a backlog pointer.
- Update `TODO.md` to point hint planning at `ROADMAP.md`.
- Move documentation files (changelog, roadmap, todo, style guides, and legacy docs)
  into `docs/` to reduce root-level clutter.
- Split `README.md` into shorter sections with links to new docs.
- Rename `docs/INSTALLATION.md` to `docs/INSTALL.md` and
  `docs/DEVELOPER.md` to `docs/DEVELOPMENT.md`.

### Removed
- Remove legacy `docs/TODO.txt` and `docs/old_README.md` in favor of updated docs.

## 2025-12-12

### Added
- Add `qti_package_maker/common/tabulate_compat.py` with a fallback plain-text table renderer.
- Add HTML `<table>` to plain-text conversion in `qti_package_maker/common/string_functions.py`.

### Changed
- Use `tabulate_compat` in `qti_package_maker/assessment_items/item_bank.py` and
  `qti_package_maker/engines/engine_registration.py`.
- Pass `allow_mixed` through `qti_package_maker/package_interface.py` when supported, and
  forward it in `qti_package_maker/engines/text2qti/engine_class.py` and
  `qti_package_maker/engines/bbq_text_upload/engine_class.py`.
- Allow table markup in `qti_package_maker/engines/human_readable/write_item.py` content checks.

### Removed
- Remove unused variables in `qti_package_maker/engines/text2qti/write_item.py`.
- Remove unnecessary `global` declarations in `qti_package_maker/common/franken_bptools.py`.

### Chore
- Ignore `pyflakes.txt` in `.gitignore`.
- Mark tests executable: `tests/test_bbq_converter_all_types.py` and
  `tests/test_human_readable_tables.py`.
