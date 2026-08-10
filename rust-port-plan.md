# Plan: Rust port of qti-package-maker

## Context

`qti-package-maker` converts question banks between LMS assessment formats: it reads BBQ text,
text2qti, Oklahoma Christian BQGen, and Blackboard Original pool-export ZIPs, and writes ten
output formats including Canvas QTI 1.2, Blackboard QTI 2.1, Blackboard pool-export ZIP,
Moodle Aiken, human-readable text, YAML, and a self-contained HTML self-test page. The Python
package is mature (~13k lines of shipping code, ~120 test modules) and its hardest lessons are
already encoded: the frozen `media_assets` image API, the four-value `media_policy` contract,
the shared `zip_writer` archive-map, and `package_integrity.py`, a cross-reference checker that
reproduces two real Blackboard import failures as regression canaries.

The port exists because the Python design has hit a structural ceiling that no amount of Python
refactoring removes. Engine capability is decided by `inspect.getsource(method)` string-searching
for `"raise NotImplementedError"`. Item-type dispatch is `getattr(write_item_module, item.item_type)`
on a class name. Validation is `getattr(validator, f"validate_{item_type}")`. Engines are found by
`pkgutil.iter_modules` scanning a directory. Every one of those is a runtime string lookup that
fails at the moment a user runs a conversion, and none of them can tell an author "you added an
item type and forgot engine X" until that exact item hits that exact engine. A Rust port turns all
four into compile-time facts: an exhaustive `match` over an item enum, a registry that is a
readable list, and `Option<fn>` capability that is structurally true rather than sniffed.

Image handling is the port's highest-risk surface and gets its own contract section below. Images
cross every boundary in the system: they are authored as relative paths, resolved against a base
directory, renamed for collision safety, rewritten into five different platform-specific `src`
spellings by five different writers, packaged as ZIP entries, cross-referenced from a manifest, and
in one case recovered back out of a Blackboard package into files on disk. Every one of those steps
is a place where "the image still works" and "the bytes are identical" come apart.

The intended outcome is a fresh Rust repository that reaches feature parity with the Python
package's conversion behavior, ships a single static `bbq-converter` binary with no Python runtime,
and exposes a core library whose public API is shaped so PyO3 bindings can be added later without
reworking it.

## Objectives

- Deliver a Rust workspace that reads all four input formats and writes all ten output formats at
  semantic parity with the Python package.
- Replace every runtime string dispatch (engine discovery, item-type dispatch, validator lookup,
  capability sniffing) with a compile-time construct that fails to build rather than fails to run.
- Ship one `bbq-converter` binary whose CLI surface matches `tools/bbq_converter.py` so existing
  educator muscle memory and shell scripts keep working.
- Establish one named authority for what "semantic parity" means, so a divergence has exactly one
  correct resolution.
- Define one media contract covering every engine and every image source kind, so image behavior is
  a property of the system rather than of whichever fixture happened to be tested.
- Keep the `qti-core` public API owned-value and lifetime-free so a PyO3 binding crate is additive.

## Design philosophy

Adaptability is the governing constraint: the system must absorb new item types, new engines, and
new LMS quirks over years without the cost of each addition growing. In Rust that means the type
system carries the invariants that Python carries in convention. One `ItemBody` enum with seven
variants means adding an eighth makes the compiler enumerate every writer that must grow a new
arm; the Python equivalent silently prints `Warning: No write function found` and drops the item.
This is the repo's **fix the design, not the symptom** principle applied at the language level, and
it is why the port is worth its cost rather than being a translation exercise.

The plan is decomposed into fourteen tightly scoped milestones. Each milestone owns one design
decision and one verifiable artifact, so progress is visible, a stall is localized, and no milestone
can quietly carry several unresolved decisions inside it. Two milestones exist purely to be serial
bottlenecks: M7 freezes the engine traits, and M6 establishes the integrity oracle and proves it
against an independent implementation before anything the port produces is measured by it. Both
would be invisible checkpoints inside a larger milestone; as milestones they either pass or block.
This follows **atomic task decomposition**: one owner, one clear outcome, one verification step.

The port matches Python's behavior exactly and records every improvement idea in `docs/ROADMAP.md`
for a later plan. Stable choice identifiers are the clearest case: Rust makes them natural, Python
derives identifiers from list position at render time, and so this port derives them from list
position too. Shipping at parity is what makes the port swappable; the improvements land afterward,
on a foundation that the compiler now guards.

Rejected alternative: transliterating the Python module-per-item-type layout into Rust modules with
`HashMap<String, fn(&Item) -> String>` dispatch. It would port faster and preserve the file map
one-to-one, but it reproduces the exact runtime-lookup ceiling that motivates the port, and it
makes the compiler blind to an unhandled item type. Rejected on the same grounds the port exists.

- Evidence strategy for uncertain methods: three crate selections (HTML rewriting, XML, YAML) plus
  number spelling, and one behavioral question (CRC16 byte agreement), are resolved by measurement
  rather than by preference. Crate selections resolve in M1 before any dependent milestone starts;
  the CRC question resolves in M2 against the repo's own question corpus. Each has a stated decision
  rule and a fallback that keeps its dependents moving.

## Scope

- Create a fresh git repository named `qti-package-maker-rs` with a Cargo workspace: `qti-core`,
  `qti-integrity`, `qti-engines`, `qti-cli`, plus an `xtask` runner.
- Port the item model (7 types), validator, `ItemBank`, `string_functions`, and CRC16-XMODEM identity.
- Port `media_assets` (frozen API), `zip_writer`, and `qti_manifest`.
- Implement the media contract in full: the engine-by-source-kind behavior table, collision and
  dedup rules, lifetime ownership, provenance-carrying diagnostics, and the extension boundary.
- Port `package_integrity.py` as `qti-integrity`, add the item-HTML-to-manifest-to-ZIP-entry trace
  check, cross-validate against the Python checker on valid and corrupted packages, and record each
  check's provenance.
- Define `ItemFingerprint`, comparing every item field, with media compared by resolved content and
  placement.
- Port all ten shipping engines: `bbq_text_upload`, `text2qti`, `okla_chrst_bqgen`,
  `blackboard_export_zip`, `canvas_qti_v1_2`, `blackboard_qti_v2_1`, `moodle_aiken`,
  `human_readable`, `exam_yaml`, `html_selftest`.
- Port the four reader paths, including the pool reader's csfiles and hotspot image recovery.
- Build the `bbq-converter` binary with the existing flag surface, plus a `qti-package-maker`
  binary for engine and item-type introspection and package checking.
- Build `cargo xtask` commands for the three cross-language checks: CRC corpus agreement, oracle
  cross-validation, and the differential parity harness with a per-format comparison.
- Scaffold the new repo to house style: `REPO_TYPE=rust`, `AGENTS.md`, `docs/`, `docs/CHANGELOG.md`.

## Non-goals

- Leave `color_theory/` (~1900 lines, `seaborn` + `colour-science` + CAM16), `anti_cheat.py`, and
  `franken_bptools.py` in Python. No engine imports them; they are utility exports consumed by the
  sibling `biology-problems` repo, so the port succeeds without them and the Rust dependency tree
  stays free of scientific-color libraries.
- Accept structural equivalence for XML and ZIP output. Reproducing lxml's pretty-printer,
  attribute ordering, and ZIP entry bytes would constrain the port to one XML library's quirks
  forever, and an LMS reads structure. See `## Roadmap context` for what the port ships instead.
- Convert `template_class/` into a worked example in `docs/ENGINE_AUTHORING.md`, which serves the
  same purpose as a registered no-op engine while staying out of the registry.
- Gate Rust code hygiene on `cargo fmt --check` and `cargo clippy -- -D warnings`; the Python repo's
  hygiene harness stays in Python, and the propagated Markdown and ASCII checks continue to cover
  `docs/`.
- Preserve current conversion semantics exactly. Hints, per-item feedback, stable choice identifiers,
  seeded shuffle, and per-engine feature gates are named in `## Roadmap context` with the reason this
  version succeeds without each one.
- Leave the Python repository running and unmodified, so downstream Python callers keep working
  throughout.

## Current state summary

| Area | Python shape | Port consequence |
| --- | --- | --- |
| Item types | 7 classes in `item_types.py`, `item_type` = class name string | One `ItemBody` enum; exhaustive `match` |
| Validation | `getattr(validator, f"validate_{type}")` at `__init__` | Fallible constructors returning `Result<Item, ValidationError>` |
| Identity | CRC16-XMODEM of question + a per-type secondary string | `ItemCrc` newtype; bank keying and dedup only |
| Bank equality | `ItemBank.__eq__` compares key SETS, explicitly order-independent (`item_bank.py:606-624`) | Round-trip compares fingerprint sets, matching that contract |
| Item ordering | insertion order preserved; `item_number` assigned from it by `renumber_items()` | Order checked separately, for formats that carry it |
| Choice identity | identifiers derived from list position at render time (`answer_{idx}`, `choice_{j+1:03d}`) | Choices are plain strings; the port derives identifiers at render time too |
| Engine registry | `pkgutil` directory scan + `importlib` | Explicit `&[EngineEntry]` slice in one greppable file |
| Capability | `inspect.getsource` searched for `"raise NotImplementedError"` | `Option<fn(...) -> Box<dyn Writer>>`; `is_some()` |
| Render dispatch | `getattr(write_item_module, item.item_type)` | Trait method with an exhaustive match |
| Media | `media_assets.py`, frozen API, 4 policy string constants | Near 1:1 port; `MediaPolicy` enum makes the invalid-policy case unrepresentable |
| Packaging | stage into timestamped CWD dir, zip, `rmtree` | In-memory `ArchiveMap`; the staging-directory leak class disappears |
| Integrity | `package_integrity.py`, 846 lines, regression canaries | Ported in M6, extended with a trace check, cross-validated, provenance-annotated |

### What the CRC does not cover

`item_crc16` is `question_crc16 + "_" + secondary_crc16`, and the secondary string is per-type
(`item_types.py:148-230`):

| Type | Secondary string | Fields excluded from identity |
| --- | --- | --- |
| MC | `"|".join(choices_list)` | **`answer_text`** |
| MA | `"|".join(choices_list)` | **`answers_list`**, `min_answers_required`, `allow_all_correct` |
| MATCH | `"|".join(prompts+choices)` | the prompt/choice boundary position |
| NUM | `f"{answer:.2e}_{tol:.2e}"` | `tolerance_message` |
| FIB | `"|".join(answers_list)` | none |
| MULTI_FIB | sorted `k:v` pairs | none |
| ORDER | `"|".join(ordered_answers)` | none |

Two MC items with the same question and the same choices but *different correct answers* carry the
same `item_crc16`. A round-trip test asserting CRC-set equality would therefore pass a reader that
corrupted every correct answer in the bank. `ItemFingerprint` exists because of this. The CRC keeps
its Python role -- bank keying and dedup -- and serves as a cheap pre-filter.

### On the absent feedback field

`BaseItem` sets `feedback_correct` and `feedback_incorrect` to `None` and no engine reads them,
while `text2qti/read_package.py:79` attaches `choice_feedback` and `answer_feedback` attributes to
item instances that no writer consumes. The port carries no feedback field: the Rust text2qti reader
parses those lines and discards them, matching the observable behavior today.

## Media contract

This section is the specification `qti-core::media` and every engine implement. It is the answer to
"is image handling semantic, or does it merely pass today's fixtures."

### Image sameness across a round trip

Two images are the same when their **content hash and placement** match. Content is the sha256 of
the asset's bytes (`compute_content_hash`). Placement is the field the reference sits in plus its
ordinal position within that field.

Excluded from sameness, deliberately: filename, in-content `src`, resolved path, output name, and
pixel dimensions. Each varies legitimately across a correct round trip. MIME type is excluded as a
separate term because it is derived from the extension and content already determines it; a file
renamed `.jpg` to `.jpeg` with identical bytes is the same image.

What this catches: a dropped image, a swapped pair within one field, an image moved from a choice to
the question stem, and any byte-level corruption. What it permits: renaming, relocation, and every
platform-specific `src` spelling.

Ownership follows the milestone graph: M2 defines `MediaRef { content_hash, field, ordinal }` and
the comparison over it, taking resolved refs as input; M4 supplies the resolver that produces them
from real assets. M2 stays filesystem-free and independent of the media layer.

### Expected rewrites that must not fail parity

Each of these is a correct transformation of the same image, and the fingerprint passes all of them:

| Original `src` | Becomes | Where |
| --- | --- | --- |
| `images/foo.png` | `../media/foo.png` | `canvas_qti_v1_2`, relative variant |
| `images/foo.png` | `$IMS-CC-FILEBASE$/media/foo.png` | `canvas_qti_v1_2`, filebase variant |
| `images/foo.png` | `@X@EmbeddedFile.requestUrlStub@X@bbcswebdav/xid-7_1` | `blackboard_export_zip` write |
| `@X@...bbcswebdav/xid-7_1` | `foo.png` | `blackboard_export_zip` read, from the LOM sidecar |
| `images/foo.png` | `data:image/png;base64,...` | `html_selftest` |
| `images/foo.png` | `[image: foo.png]` | `human_readable`, `moodle_aiken` (placeholder policy) |

The Blackboard pair is the decisive case: a write-then-read round trip rewrites the `src` twice and
returns a different spelling by design. Comparing spelling would fail M10 every time it ran.

### Engine behavior by image source kind

Every cell is defined, so no engine has undefined behavior for any input. `package`,
`placeholder_warn`, `reference_warn`, and `fail` are the four `media_policy` values; the table says
what each policy does per kind.

| Engine | Policy | Local file | External URL | `data:` URI | Missing file | Unsupported ext |
| --- | --- | --- | --- | --- | --- | --- |
| `canvas_qti_v1_2` | package | Copy into `media/`, rewrite `src` | Keep verbatim, warn | Typed error before output | Typed error naming item and path | Typed error naming the extension |
| `blackboard_qti_v2_1` | package | Copy into the package, rewrite `src` | Keep verbatim, warn | Typed error before output | Typed error | Typed error |
| `blackboard_export_zip` | package | Copy to `csfiles/`, emit LOM sidecar, rewrite to `@X@` token | Keep verbatim, warn | Typed error before output | Typed error | Typed error |
| `html_selftest` | package | Inline as base64 `data:` URI | Keep verbatim, warn | Pass through unchanged | Typed error | Typed error |
| `human_readable` | placeholder_warn | Substitute `[image: name]`, warn | Substitute, warn | Substitute `[image: embedded image]`, warn | Typed error | Typed error |
| `moodle_aiken` | placeholder_warn | Substitute `[image: name]`, warn | Substitute, warn | Substitute, warn | Typed error | Typed error |
| `bbq_text_upload` | reference_warn | Keep `src` verbatim, warn | Keep verbatim, warn | Keep verbatim, warn | Typed error | Typed error |
| `text2qti` | reference_warn | Keep verbatim, warn | Keep verbatim, warn | Keep verbatim, warn | Typed error | Typed error |
| `okla_chrst_bqgen` | reference_warn | Keep verbatim, warn | Keep verbatim, warn | Keep verbatim, warn | Typed error | Typed error |
| `exam_yaml` | reference_warn | Keep verbatim, warn | Keep verbatim, warn | Keep verbatim, warn | Typed error | Typed error |

Two source kinds are read-side only and belong to the pool reader: `@X@...bbcswebdav/xid-N_1` tokens
resolve through the CSResourceLinks resource to a `csfiles/` binary named from its LOM sidecar, and
`<matapplication uri="<hash>/<file>">` hotspot references resolve against the pool resource's
manifest `xml:base`. Both land in the extraction directory under recovered plain filenames, so an
imported bank has the same shape as file-authored input.

SVG packages like a raster image and carries a "LMS support is not guaranteed" warning. Absolute
filesystem paths classify as local and resolve through the same traversal guard, which rejects any
path escaping the base directory.

### Collisions, dedup, and wrong-image association

Identity for output naming is the in-content `src`. `assign_output_names` sorts by `src`, walks in
that order, and appends `(1)`, `(2)` to a colliding basename, so naming is deterministic and
independent of item order or iteration order.

Three cases and their decided outcomes:

- **Two different images both named `figure.png`** (`images/figure.png`, `figures/figure.png`):
  distinct `src` values, so two package entries, `figure.png` and `figure(1).png`, each item's HTML
  rewritten to its own name. Sorted-by-`src` assignment is what makes which-gets-the-suffix stable.
- **Ten questions referencing the same `src`**: one package entry, ten rewritten references to it.
  Dedup is by `src`.
- **Two different `src` values whose files have identical bytes**: two package entries. Python keys
  on `src`, so the port does too; content-addressed dedup is in `## Roadmap context`.

### Ownership and lifetime after a read

The pool reader creates one extraction directory, copies every recovered binary into it, and hands
ownership to the returned bank via the `MediaBaseDir` RAII type. The files live exactly as long as
the bank does and are removed when it drops. A bank pointed at a directory it did not create leaves
that directory alone. A merge carries the surviving directory forward without transferring
ownership, so the one owning bank frees it exactly once.

### Diagnostics carry provenance

Every media warning and every media error names five things: the engine, the item CRC, the original
in-content `src`, the resolved path or token it mapped to, and the action taken (packaged, kept
verbatim, substituted, or rejected). `MediaWarning` gains `resolved` and `action` fields over the
Python original, which is an additive change to a diagnostic type rather than a behavior change.

### One failing image in a multi-image item

The whole bank is rejected before any output is written, and the error names the item CRC and the
offending `src`. This matches Python, where `collect_assets()` resolves every asset across the bank
up front and a missing file raises there, and where `raise_on_unpackagable_media()` scans the whole
bank before `save_package()` creates anything. Rejecting early is what keeps a failed run from
leaving a half-written package behind. Warnings, by contrast, are per-asset and never halt a run.

### Writers and readers share the layer without forced symmetry

The shared core is the `MediaAsset` record and the four operations both directions need: classify,
resolve, hash, and rewrite HTML. Writers add "resolve a source file into a package asset" on top;
the pool reader adds "recover a package asset into a source file" on top. Those two directions live
in their own modules (`media::package` and the reader's `read/media_*.rs`) rather than as branches
inside shared functions, so neither accumulates the other's special cases.

The extension test, applied whenever the media layer changes: adding a new image mechanism (a new
LMS resource scheme, remote fetching, image metadata) should touch `media.rs` plus the one engine
that uses it. Touching most engines means the boundary has drifted and belongs back in review.

## Parity authority

Four sources can disagree about correct behavior. When they do, this order decides, highest first.
A work package that finds a divergence reports it and continues; `architect` applies this order and
records the outcome in `docs/CHANGELOG.md` under `### Decisions and Failures`.

1. **Observed LMS import behavior.** Rare and expensive, but it is ground truth. The two Blackboard
   import failures already recorded in the Python repo are in this tier.
2. **`qti-integrity` violations from a check with recorded provenance.** A check earns tier 2 when
   M6 records where it came from: a specific LMS failure, or an invariant the package format
   requires (a manifest `href` must resolve; a `correctResponse` must name a declared choice in the
   same item). Provenance is recorded per check in `docs/PARITY.md`.
3. **Python runtime behavior on the same input.** The port's contract. Where the two differ with no
   tier-1 or tier-2 signal, Python's behavior is correct and the Rust side matches it.
4. **Everything else**, in descending weight: `qti-integrity` checks lacking recorded provenance,
   which are advisory; then Python test assertions, which can encode brittle expectations. A Rust
   test may legitimately differ from its Python counterpart when the Python assertion checks a
   collection length, a key list, or a tunable constant.

Tier 4's first entry keeps the checker from becoming a specification by accident. The Rust oracle is
a port of Python logic; a check nobody can trace to an LMS failure or a format requirement is a
useful smoke signal, and Python's actual behavior outranks it.

Standing rule: a coder who finds a divergence reports it with both values and moves on to the next
item; `architect` decides. Improvement ideas go to `docs/ROADMAP.md` and the port ships at parity.

## Architecture boundaries and ownership

```
qti-package-maker-rs/
  Cargo.toml                 # workspace
  REPO_TYPE                  # "rust"
  VERSION
  crates/
    qti-core/                # item, fingerprint, validate, bank, strings, crc, media, zip, manifest
    qti-integrity/           # package_integrity port; depends on std + the XML crate
    qti-engines/             # all 10 engines, one registry file
    qti-cli/                 # bbq-converter + qti-package-maker binaries
  xtask/                     # cross-language checks: crc-corpus, oracle-crosscheck, parity
  tests/                     # workspace integration tests
    fixtures/
      bb_export_slice.zip    # the one committed binary fixture (see Test classification)
  docs/
```

`qti-integrity` depends on neither `qti-core` nor `qti-engines`, so it reads finished packages from
disk and judges Python and Rust output on equal terms. That independence is what makes it usable as
a cross-implementation check. `qti-engines` depends on `qti-core`; `qti-cli` depends on all three.

The registry is a hand-written slice in one file, so the engine list is greppable in one place. The
Python repo's own style rules keep discovery logic where coders look for it, and that judgment
carries over.

### Engine trait shape, decided

The registry holds engines as trait objects, so the traits it names are object-safe and carry no
associated types. The per-item render generic lives one level below, as a free function each engine
calls from inside its own `save_package`:

```rust
// Object-safe. This is what the registry stores.
pub trait Writer {
    fn name(&self) -> &'static str;
    fn media_policy(&self) -> MediaPolicy;
    fn supported_kinds(&self) -> &'static [ItemKind];
    fn save_package(&self, bank: &ItemBank, outfile: Option<&Path>)
        -> Result<PathBuf, EngineError>;
}

// Object-safe. ReadOutcome is a concrete struct: { bank, warnings }.
pub trait Reader {
    fn name(&self) -> &'static str;
    fn read_items(&self, infile: &Path, allow_mixed: bool)
        -> Result<ReadOutcome, EngineError>;
}

// The shared render loop, generic over the engine's own rendered type.
// Monomorphized at each engine's call site; never a trait object.
pub fn render_bank<R>(
    bank: &ItemBank,
    render_item: impl Fn(&Item) -> Result<Option<R>, EngineError>,
    hooks: RenderHooks<'_>,
) -> Result<Vec<R>, EngineError>;
```

`R` is the engine's private choice: an XML element tree for the QTI engines, `String` for the text
engines. `RenderHooks` carries the optional pre-render and post-render closures that port
`BaseEngine.process_item_bank`'s two hooks. Every engine shares one render loop, and the boundary
the registry sees stays object-safe. `EngineError` is a `thiserror` enum wrapping validation, media,
XML, and I/O failures plus `UnsupportedItemKind { kind, engine }`.

Registry entries name constructors returning those trait objects, so capability is structural:

```rust
pub struct EngineEntry {
    pub name: &'static str,
    pub media_policy: MediaPolicy,
    pub make_writer: Option<fn() -> Box<dyn Writer>>,
    pub make_reader: Option<fn() -> Box<dyn Reader>>,
}
```

M7 confirms this compiles and carries all three probes before any fan-out.

### Mapping (milestones / workstreams -> components / patches)

| Milestone / Workstream | Component | Review boundary |
| --- | --- | --- |
| M1 | repo root, `Cargo.toml`, spike crate | Workspace compiles; crate decisions recorded with evidence |
| M2, M3 | `qti-core/src/{item,fingerprint,crc,strings,validate,bank}` | Public API takes and returns owned values with no lifetimes |
| M4 | `qti-core/src/media/` | Implements the media contract section in full |
| M5 | `qti-core/src/{zip,manifest}` | Packages are assembled through `ArchiveMap` |
| M6 | `crates/qti-integrity`, `xtask/oracle_crosscheck.rs` | Agrees with the Python checker on valid and corrupted packages |
| M7 | `qti-engines/src/{traits,human_readable,canvas12,bbq}` | Trait shape signed off against three shapes and all four readers |
| M8 / WS-Text | `qti-engines/src/{text2qti,okla,aiken,exam_yaml}` | One engine module per work package |
| M9 / WS-Pkg | `qti-engines/src/{bb21,bb_export/write}` | Every ZIP passes `qti-integrity` clean |
| M10 | `qti-engines/src/bb_export/read/` | One named source file per sub-work-package |
| M11 | `qti-engines/src/html_selftest` | Single self-contained file |
| M12 | `qti-engines/src/registry.rs`, `crates/qti-cli` | Registry owned here exclusively |
| M13 | `xtask/parity.rs` | Every format has a semantic comparison |
| M14 | `docs/`, CI, crate metadata | Docs and CI |

## Test classification

The Python repo runs three tiers: a sub-second pytest fast lane, non-browser E2E under `tests/e2e/`
run directly, and browser tests. The Rust repo maps onto the same model, and every check named in
this plan is classified into exactly one of three homes. `docs/PYTEST_STYLE.md`'s permanent-test
checklist is the filter: a permanent test exercises logic that could plausibly be wrong, uses inline
self-contained inputs, runs offline in well under a second, and still passes next week without code
changes.

**Permanent (`cargo test`, the fast lane).** Offline, inline inputs, no subprocess, no Python.

- Pure functions: CRC values for known strings, each type's secondary-string construction, prefix
  stripping, MIME guessing, traversal rejection, collision-safe naming, number spelling.
- Each `ValidationError` variant firing on its own minimal bad input.
- Each `ItemFingerprint` sensitivity case (equal CRC / unequal fingerprint; renamed-but-identical
  bytes equal; swapped pair unequal; dropped image unequal).
- The five-case HTML rewrite subset (WP-B1), built from inline strings.
- Round-trips per readable engine, on banks built in code.
- Each ZIP-producing engine's output passing `qti-integrity`, on banks built in code.
- The integrity regression canaries and the generated negative corpus, both constructed in code.
- `MediaBaseDir` lifetime: owned directory removed on drop, caller-supplied directory untouched.

**Tooling (`cargo xtask`, run on demand and in CI).** These need the Python package installed, so
they are subprocess-driven and cross-language. They are the Rust analogue of `tests/e2e/`: valuable,
repeatable, and outside the fast lane.

- `cargo xtask crc-corpus` -- CRC agreement against Python over the repo's question corpus.
- `cargo xtask oracle-crosscheck` -- M6's two agreement runs against `package_integrity.py`.
- `cargo xtask parity` -- M13's differential harness.

**One-time proof (run, record the result in `docs/CHANGELOG.md`, then retire).** Checks that prove
the rebuild happened correctly but would only decay afterward.

- The M2 exhaustive CRC sweep over every question string in the Python repo's own corpus. Its
  permanent successor is a small set of known-value CRC unit tests; the sweep proves the port once.
- The M7 reader survey, whose output is a written finding in the trait sign-off rather than a test.

**Fixtures.** `tests/fixtures/bb_export_slice.zip` is the single committed binary fixture, kept
because a real Blackboard export's file shape is exactly the behavior under test -- the durable-fixture
exception in `docs/PYTEST_STYLE.md`. Everything else is built in code: test images are byte arrays
for a minimal valid PNG, GIF, and JPEG; the negative corpus is generated by the test that consumes
it; sample banks are constructed inline. This keeps the corpus from drifting out of existence and
keeps a missing file from taking down a whole test module.

**Grounding.** Every gate in this plan is a correctness or agreement check. The plan sets no
throughput, latency, or binary-size target, because no such requirement exists for a batch converter
that runs once per question bank, and inventing one would gate the work on an arbitrary number.

## Milestone plan

| M | Title | Summary | Goal |
| --- | --- | --- | --- |
| M1 | Workspace and dependency decisions | Four-crate scaffold plus `xtask`; resolve the HTML, XML, YAML, and number-spelling choices with evidence | Workspace builds; every external dependency is chosen and justified |
| M2 | Item model, identity, and fingerprint | `ItemBody` enum; CRC16-XMODEM; `ItemFingerprint`; `string_functions` | An item constructs, hashes to Python's CRC, and compares structurally |
| M3 | Validation and item bank | Fallible constructors; `ItemBank` with RAII media directory | A bank of validated items builds, merges, dedups, and drops cleanly |
| M4 | Media asset layer | The media contract implemented in full | Every engine-by-source-kind cell behaves as specified |
| M5 | Packaging primitives | In-memory `ArchiveMap` ZIP builder and IMS manifest generator | A ZIP and a manifest are produced entirely in memory |
| M6 | Integrity oracle | `qti-integrity` port, trace check, cross-validation, provenance | The oracle agrees with an independent implementation before judging Rust output |
| M7 | Engine trait spike | Traits proven by a text writer, a ZIP writer, and a reader | Trait shape signed off; fan-out is safe |
| M8 | Text-format engines | Four remaining text engines, two of them readers | Every text format writes; both remaining text readers round-trip |
| M9 | QTI package writers | Blackboard QTI 2.1 and Blackboard pool-export writers | Both produce ZIPs that pass `qti-integrity` clean |
| M10 | Blackboard pool reader | Five atomic sub-deliverables, one source file each | A written pool reads back to an identical fingerprint set |
| M11 | HTML self-test engine | Single-file HTML with inline CSS, JS, and base64 images | Output is self-contained and grades all seven item kinds |
| M12 | Registry and CLI | Compile-time registry; both binaries | The binary converts a real bank to all ten formats |
| M13 | Parity harness and integration gate | Differential Python-vs-Rust runner with a per-format comparison | Zero semantic divergences; all round-trips hold |
| M14 | Repo and release readiness | Docs, CI, crate metadata, release lane | Repo satisfies house style; binaries build on macOS and Linux |

### Milestone: M1 workspace and dependency decisions

- Depends on: none.
- Deliverables: WP-A0, WP-F3.
- Entry criteria: none.
- Automated exit criteria: `cargo build` succeeds across the workspace; `REPO_TYPE` contains `rust`;
  chosen crate versions are pinned.
- Review exit criteria: `docs/DEPENDENCY_DECISIONS.md` records all four decisions with the command
  run and the observed result.
- Parallel-plan ready: yes. WP-A0 and WP-F3 are independent.

### Milestone: M2 item model, identity, and fingerprint

- Depends on: M1.
- Deliverables: WP-A1, WP-A2.
- Entry criteria: workspace builds.
- Automated exit criteria: all seven item variants construct; `field_strings()` yields every
  HTML-bearing leaf; the fingerprint sensitivity tests pass; `cargo xtask crc-corpus` reports full
  agreement with Python.
- Review exit criteria: `architect` signs off on the enum shape; the one-time CRC sweep result is
  recorded in `docs/CHANGELOG.md`.
- Parallel-plan ready: yes. WP-A1 and WP-A2 touch disjoint files.

### Milestone: M3 validation and item bank

- Depends on: M2.
- Deliverables: WP-A3, WP-A4.
- Entry criteria: the item model is signed off.
- Automated exit criteria: every construction path runs validation; each `ValidationError` variant
  has a test that fires it; bank merge, dedup, slice, trim, and renumber match Python behavior; the
  `MediaBaseDir` lifetime tests pass.
- Parallel-plan ready: no. WP-A4 consumes WP-A3's constructors; a short serial pair.

### Milestone: M4 media asset layer

- Depends on: M2; M1 (HTML crate decision).
- Deliverables: WP-B1.
- Entry criteria: the HTML crate is chosen and pinned.
- Automated exit criteria, scoped to behaviors that could realistically regress rather than to
  every table cell: each of the four policies produces its specified outcome against each of the
  three source kinds (twelve cases at the media layer, not fifty at the engine layer -- each engine
  verifies its own row once in its own milestone); the collision, dedup, and repeated-reference
  cases pass; missing media and unsupported extension produce typed errors naming the item and the
  path; the permanent HTML rewrite subset passes; diagnostics carry all five provenance fields;
  end-to-end fingerprinting over real files on disk produces the `MediaRef` values M2's comparison
  expects.
- Review exit criteria: `architect` confirms the writer and reader directions live in separate
  modules over a shared core, per the media contract's extension test.
- Parallel-plan ready: no. One cohesive module whose invariants travel together.

### Milestone: M5 packaging primitives

- Depends on: M4; M1 (XML crate decision).
- Deliverables: WP-B2, WP-B3.
- Entry criteria: the XML crate is chosen and pinned.
- Automated exit criteria: `build_zip` writes sorted entries and explicit empty-directory markers;
  `generate_manifest` produces QTI 1.2 and 2.1 manifests with correct namespaces, webcontent
  resources, and dependency links; the generated manifest parses, and M5's own local self-consistency
  check confirms every `href` and `identifierref` it emitted names something it also emitted.
  M5 owns structural construction and proves it locally; the trusted oracle is applied from M7
  onward, once M6 has cross-validated it. This keeps M5 and M6 genuinely concurrent, with no
  dependency running backwards between them.
- Parallel-plan ready: yes. WP-B2 and WP-B3 are independent.

### Milestone: M6 integrity oracle

- Depends on: M1 (XML crate decision). Independent of M2-M5, and runs concurrently with them.
- Deliverables: WP-B4.
- Entry criteria: the XML crate is chosen and pinned.
- Automated exit criteria:
  - `tests/fixtures/bb_export_slice.zip` passes with zero violations.
  - The **media trace check** passes: for every packaged image, the oracle follows the chain from the
    item HTML `<img src>`, through the manifest `<file href>` and `<dependency identifierref>`, to a
    real ZIP entry with readable image bytes, and reports a violation when any link is missing. This
    is the check that catches a structurally valid package whose image an LMS cannot actually load.
  - The generated negative corpus is rejected, one deliberately corrupted package per check
    category: dangling manifest `href`, dangling `dependency identifierref`, QTI 1.2 `varequal`
    naming an undeclared choice, QTI 2.1 `correctResponse` naming an undeclared choice, missing QTI
    2.1 outcome declaration, `<img src>` with no matching ZIP entry, image present in the ZIP but
    absent from the manifest, truncated raster header, single-pixel image, unsafe identifier, orphan
    `bbcswebdav/xid-N` token, CSResourceLinks `parentId` with no matching `bbmd_asi_object_id`, and
    csfiles binary missing its LOM sidecar.
  - The four ported regression canaries still detect their bug class.
  - `cargo xtask oracle-crosscheck` reports identical violation lists against Python
    `package_integrity.check_package()` on both corpora: the valid corpus (packages the *Python*
    engines produce, plus every real export under `SAMPLES/` and `tests/fixtures/`) and the negative
    corpus. No Rust engine output appears in either, so a shared producer-checker bug cannot form
    here, and agreeing on independently constructed defects proves the two implementations do not
    share an omission.
- Review exit criteria: `reviewer` audits the module independently, asking specifically whether any
  check was derived from the Rust producer's assumptions rather than from the Python checker's logic
  and the format specifications. Each check is annotated with its provenance, which decides its tier
  under the parity authority; the annotations become `docs/PARITY.md`.
- Parallel-plan ready: no. One module whose value is being a single trusted authority.

**Dimension check scope, decided, and its two halves given different tiers.**
`_check_image_dimensions` does two things, and they are not equally well founded.

- **Unreadable raster header: structural, tier 2.** A truncated or corrupt file that no parser can
  read is objectively defective packaging and an LMS renders it as a broken image. It reads magic
  bytes first and falls back to the extension, so a mislabeled file is still checked.
- **Minimum visible size: advisory, tier 4.** Flagging a small-but-valid raster is a judgment about
  intent, not a structural fact, and it would reject a legitimate 8x8 icon or an inline instructional
  marker. Neither an observed LMS failure nor a format requirement backs it, so under this plan's own
  provenance rule it cannot be tier 2. The port keeps the check, because Python has it and tier 3
  says match Python, and records it as advisory so it never overrules real Python behavior or blocks
  a package on its own.

This is the provenance mechanism doing its job on the first check to need it. Vector images carry no
raster header and are excluded by the extension filter; SVG's defined behavior is the
packaged-with-a-warning path in the media contract. Large images are valid and pass.

### Milestone: M7 engine trait spike

- Depends on: M3, M4, M5, M6.
- Deliverables: WP-G0.
- Entry criteria: core, media, packaging, and a cross-validated oracle are complete.
- Automated exit criteria: the object-safe trait shape above compiles with a populated
  `&[EngineEntry]` registry holding `Box<dyn Writer>` and `Box<dyn Reader>` for all three probes --
  this is the first thing built, since a registry that cannot hold its engines invalidates
  everything downstream. Then three deliberately dissimilar probes work end to end:
  `human_readable` (text write, `R = String`, placeholder policy), `canvas_qti_v1_2` (ZIP write,
  `R` = XML element, package policy, media rewriting, ZIP passing `qti-integrity` clean), and
  `bbq_text_upload` (read and write, round-tripping by `ItemFingerprint`). Both writers drive the
  shared `render_bank` loop with its pre-render and post-render hooks, proving one generic loop
  serves two different `R` types under one object-safe boundary.
- Review exit criteria: `architect` signs off, having completed the reader survey below and recorded
  its findings.
- Parallel-plan ready: no, deliberately. Freezing the trait wrongly is the most expensive available
  error, and its own milestone means it blocks visibly rather than propagating into eight packages.

**Reader survey required before sign-off.** The BBQ probe is the simplest of the four readers.
Before signing off, `architect` reads all four Python readers and records answers to four questions,
so the `Reader` trait generalizes rather than encoding Blackboard's shape:

- **Warning accumulation.** Which readers emit per-record warnings, and does each carry enough
  context to be actionable?
- **Skipped records.** Which readers continue past a bad record and which stop? The pool reader skips
  an unparseable item and an unknown `bbmd_questiontype` and still succeeds; the trait accommodates
  both stances.
- **Source location.** What granularity each reader can report (byte offset, line number, item
  identifier, resource name), so the warning type serves all four.
- **Fatal versus recoverable.** Where each reader draws that line. A missing manifest pool entry is
  fatal for the pool reader; the equivalent is established for each text reader.

Plus the pool reader's two structural requirements: the returned bank owns an extraction directory
whose lifetime outlives the read call and is freed by dropping the bank, and one input file can hold
multiple pool resources that merge into one returned bank. When the trait cannot express what the
survey finds, M7 blocks and the trait is revised. That is the milestone working.

### Milestone: M8 text-format engines

- Depends on: M7.
- Deliverables: WP-C2, WP-C3, WP-C4, WP-C6.
- Workstreams: WS-Text.
- Entry criteria: trait sign-off.
- Automated exit criteria: all four engines write every item kind their Python counterpart supports;
  unsupported kinds return `UnsupportedItemKind` naming the kind and the engine; each engine's row of
  the media table is verified end to end; both readers round-trip to an identical `ItemFingerprint`
  set.
- Parallel-plan ready: yes. Four independent doers, one engine module and one test file each.

### Milestone: M9 QTI package writers

- Depends on: M7.
- Deliverables: WP-D2, WP-D3.
- Workstreams: WS-Pkg.
- Entry criteria: trait sign-off.
- Automated exit criteria: each engine, given an MC+MA+MATCH+NUM+FIB bank with one embedded image,
  produces a ZIP passing `qti-integrity` with zero violations including the media trace check; the
  three collision cases from the media contract produce correctly associated images; each item's
  answer references name a choice identifier declared in that same item.
- Parallel-plan ready: yes. Two independent doers. Runs concurrently with M8 and M11.

### Milestone: M10 Blackboard pool reader

- Depends on: M9 (WP-D3, the round-trip counterpart).
- Deliverables: WP-D4a through WP-D4e, one source file each.
- Entry criteria: the pool writer is complete.
- Automated exit criteria: every sub-deliverable's row below, ending with a WP-D3 write followed by
  an M10 read yielding an identical `ItemFingerprint` set with byte-matching recovered images.
- Review exit criteria: `reviewer` audits the milestone independently.
- Parallel-plan ready: partially, split by source file so concurrency is real. `read/discovery.rs`
  (WP-D4a) lands first. `read/types_core.rs` (WP-D4b) and `read/types_extra.rs` (WP-D4c) each own
  their own file and register their types through a small dispatch table `discovery.rs` exposes, so
  they run concurrently without editing each other's code. `read/media_csfiles.rs` (WP-D4d) and
  `read/media_hotspot.rs` (WP-D4e) are likewise disjoint and concurrent once WP-D4a lands.

| Sub-WP | Source file | Deliverable | Independently verifiable by |
| --- | --- | --- | --- |
| WP-D4a | `read/discovery.rs` | ZIP/dir acceptance, `imsmanifest.xml` pool location, multi-resource merge, extraction directory, the type-registration table | Locating and counting every `<item>` in `bb_export_slice.zip`, reporting each one's declared type |
| WP-D4b | `read/types_core.rs` | Item envelope, `mat_formattedtext` recovery, MC, MA, FIB, True/False | Those four types parse from the fixture with correct answers |
| WP-D4c | `read/types_extra.rs` | NUM tolerance window, MULTI_FIB per-blank keys, MATCH pairing recovery | Those three types parse; MATCH prompt-to-choice pairing asserted explicitly |
| WP-D4d | `read/media_csfiles.rs` | `@X@` tokens, `res00005` cross-check, LOM sidecar naming, HTML rewrite | A pool with a csfiles image yields byte-matching recovered bytes |
| WP-D4e | `read/media_hotspot.rs` | `matapplication` URIs against the manifest `xml:base`, shared collision-safe naming | A pool with a hotspot image yields byte-matching recovered bytes |

WP-D4a delivers working discovery on its own: given the fixture it reports every item and its
declared type, which is verifiable behavior rather than scaffolding.

### Milestone: M11 HTML self-test engine

- Depends on: M7.
- Deliverables: WP-E1.
- Entry criteria: trait sign-off.
- Automated exit criteria: all seven item kinds render and grade; every `src` and `href` in the
  output is a `data:` URI or a document-internal reference; the MkDocs Material light/dark CSS
  variable mapping is preserved.
- Parallel-plan ready: no, internally. Runs concurrently with M8 and M9.

### Milestone: M12 registry and CLI

- Depends on: M8, M9, M10, M11.
- Deliverables: WP-F1, WP-F2.
- Entry criteria: every engine is complete and has reported its constructor signature.
- Automated exit criteria: the registry lists every engine exactly once with structurally correct
  `can_read`/`can_write`; name resolution implements exact-then-unique-prefix with an ambiguity
  error listing candidates; `bbq-converter -i <bank> --all` produces ten outputs; three CLI failure
  modes exit non-zero with actionable stderr.
- Parallel-plan ready: no. WP-F2 consumes WP-F1.

### Milestone: M13 parity harness and integration gate

- Depends on: M12.
- Deliverables: WP-F4, plus the integration gate run.
- Entry criteria: the CLI works end to end.
- Automated exit criteria: `cargo xtask parity` reports zero semantic divergences across the corpus
  using the per-format comparison table in WP-F4; the full workspace `cargo test`,
  `cargo fmt --check`, and `cargo clippy -- -D warnings` are clean; every ZIP-producing engine's
  output passes `qti-integrity`; all four readers round-trip by `ItemFingerprint`, and bank order
  matches for the formats that preserve it.
- Parallel-plan ready: no. This is the measurement milestone.

### Milestone: M14 repo and release readiness

- Depends on: M13.
- Deliverables: WP-G1, WP-G2.
- Entry criteria: the integration gate is green.
- Automated exit criteria: the documentation set is complete, its Markdown links resolve, and its
  content is ASCII; CI is green on a clean clone on macOS and Linux; `cargo build --release`
  produces a binary on both; crate metadata carries LGPLv3, the repository URL, and a CalVer version
  synchronized with `VERSION`. Every criterion runs unattended.
- Parallel-plan ready: yes. WP-G1 and WP-G2 are independent.

## Workstream breakdown

Two milestones have genuine parallel lanes; the rest are short enough that a single owner is the
cheaper coordination model.

### Workstream: WS-Text (M8)

- Goal: the four remaining text-output engines and their two readers.
- Owner: `coder`, one fresh subagent per work package.
- Work packages: WP-C2, WP-C3, WP-C4, WP-C6.
- Needs: M7 sign-off; `qti-core::media`.
- Provides: `text2qti`, `okla_chrst_bqgen`, `moodle_aiken`, `exam_yaml`.
- Review boundary, when modifying the repository: each package owns one engine module plus its own
  test file, and reports its constructor signature to WP-F1, which owns `registry.rs`.

### Workstream: WS-Pkg (M9)

- Goal: the two remaining IMS content-package writers.
- Owner: `expert_coder`, one fresh subagent per work package.
- Work packages: WP-D2, WP-D3.
- Needs: M7 sign-off; `qti-core::{media, zip, manifest}`; `qti-integrity`.
- Provides: `blackboard_qti_v2_1`, `blackboard_export_zip` (write).
- Review boundary, when modifying the repository: each engine assembles its package by building an
  `ArchiveMap` in memory and handing it to `qti-core::zip`.

## Work packages

### Work package: WP-A0 repository and workspace scaffold

- Owner: `maintainer`.
- Touch points: repo root, `Cargo.toml`, `REPO_TYPE`, `VERSION`, `AGENTS.md`, `docs/CHANGELOG.md`,
  `.gitignore`, `xtask/`.
- Depends on: none.
- Acceptance criteria: `cargo build` succeeds across the workspace; `REPO_TYPE` contains `rust`;
  `AGENTS.md` points at `docs/` per house style; `cargo xtask --help` runs.
- Obvious follow-ons: copy this plan to `docs/active_plans/active/rust_port_plan.md` and seed
  `refactor_progress.md` with the fourteen milestones.

### Work package: WP-F3 dependency spikes

- Owner: `coder`.
- Touch points: a spike crate outside the workspace; outcome recorded in
  `docs/DEPENDENCY_DECISIONS.md`.
- Depends on: none (runs concurrently with WP-A0).
- Acceptance criteria: four decisions recorded, each with the command run and the observed result.
  - **HTML scan and rewrite.** Candidates: `lol_html` (a streaming rewriter that passes untouched
    content through byte-for-byte, matching the contract `rewrite_html_srcs` states) and
    `scraper`/`html5ever` (parse to a tree, reserialize). Decision rule: choose the crate that leaves
    non-`<img>` content byte-identical across the wider syntax sweep listed in WP-B1, including
    malformed markup. `lol_html` is expected to win on that rule; the spike confirms it. This sweep
    is where those cases earn their keep; five of them graduate to permanent tests in WP-B1.
  - **XML read and write.** Candidate: `quick-xml`. Decision rule: it round-trips a real
    `imsmanifest.xml` and a real pool `.dat` from the fixture with namespaces intact and produces
    indented output. Alternative if namespaces prove awkward: `xot`, or writing over `quick-xml`'s
    low-level events.
  - **YAML.** Decision rule: choose a maintained crate that round-trips the `exam_yaml` document
    shape and has had a release within the last year; `serde_yaml_ng` and `serde_norway` are the
    leading candidates.
  - **Number spelling.** Decision rule: adopt a maintained crate covering cardinal and ordinal for
    the small-integer range in use; otherwise implement it directly (~40 lines). Roman numerals are
    implemented directly either way.
- Evidence or review, when useful: each decision names the test that produced it, so a future reader
  re-runs it when a crate changes.
- Obvious follow-ons: pin chosen versions and note the MSRV.

### Work package: WP-A1 item model and fingerprint

- Owner: `expert_coder`.
- Touch points: `qti-core/src/{item.rs, fingerprint.rs}`.
- Depends on: WP-A0.
- Acceptance criteria: `ItemCommon` + `ItemBody` enum covering MC, MA, MATCH, NUM, FIB, MULTI_FIB,
  ORDER; `ItemKind` derived from the body; `field_strings()` yielding every HTML-bearing string leaf.
  Choices are plain strings, matching Python's render-time identifier derivation. The model carries
  no feedback field.
  `ItemFingerprint` compares question text, item kind, and every supporting field including those
  the CRC omits (`answer_text`, `answers_list`, `min_answers_required`, `allow_all_correct`,
  `tolerance_message`, the MATCH prompt/choice boundary).
  **Media split, so the dependency graph matches the design.** M2 owns the comparison mechanism and
  M4 owns resolution. The fingerprint takes an already-resolved `Vec<MediaRef>` as an input
  parameter, where `MediaRef { content_hash: [u8; 32], field: FieldId, ordinal: usize }` is a plain
  data struct defined here. M2 never touches the filesystem, never hashes a file, and never depends
  on `qti-core::media`; M4 supplies the resolver that produces `MediaRef` values from real assets.
  Permanent tests, using hand-written hashes so they stay inline and offline: two MC items differing
  only in `answer_text` have equal CRCs and unequal fingerprints; the same content hash under a
  different filename compares equal; two `MediaRef` values swapped within one field compare unequal;
  a dropped `MediaRef` compares unequal; a `MediaRef` moved from the stem field to a choice field
  compares unequal.
- Evidence or review, when useful: `architect` reviews the enum shape before M3 starts.
- Obvious follow-ons: derive `serde::{Serialize, Deserialize}`, which WP-C6 consumes.

### Work package: WP-A2 string functions and CRC identity

- Owner: `coder`.
- Touch points: `qti-core/src/{strings.rs, crc.rs}`, `xtask/src/crc_corpus.rs`.
- Depends on: WP-A0.
- Acceptance criteria: CRC16-XMODEM via the `crc` crate; each item type's secondary-string
  construction matches `item_types.py` exactly, including NUM's `f"{x:.2e}"` formatting and
  MULTI_FIB's sorted key order; ASCII-only enforcement produces the same class of error on
  non-ASCII input; `strip_crc_prefix`, `strip_prefix_from_string`, `remove_prefix_from_list`,
  `number_to_letter`, `number_to_lowercase`, `number_to_roman`, `make_question_pretty`,
  `convert_sub_sup`, and the HTML-table-to-text renderer are ported.
  Permanent tests: known-value CRCs for a handful of representative strings, and one case per
  secondary-string shape. Tooling: `cargo xtask crc-corpus` compares against Python over every
  question string in the repo's corpus, and reports the first disagreement with both values.
- Evidence or review, when useful: the corpus run is M2's gating evidence and its result is recorded
  in `docs/CHANGELOG.md`. The CRC is the bank key, so agreement keeps dedup behavior identical.
- Obvious follow-ons: none.

### Work package: WP-A3 validator

- Owner: `coder`.
- Touch points: `qti-core/src/validate.rs`.
- Depends on: WP-A1.
- Acceptance criteria: one validation function per item type, invoked from the fallible constructor
  so every `Item` value has passed validation; `ValidationError` is a `thiserror` enum with a variant
  per failure mode (empty field, too few items, duplicate choice, answer absent from choices,
  MULTI_FIB key absent from the question text, MATCH prompts exceeding choices, negative tolerance);
  the HTML well-formedness check ports `clean_html_for_xml` + `validate_html`. Each error variant has
  a test that fires it on its own minimal bad input.
- Obvious follow-ons: none.

### Work package: WP-A4 item bank

- Owner: `expert_coder`.
- Touch points: `qti-core/src/bank.rs`.
- Depends on: WP-A3.
- Acceptance criteria: `ItemBank` backed by `IndexMap<ItemCrc, Item>` preserving insertion order;
  `add_item` deduplicates by CRC with a warning; `merge` implements the `media_base_dir`
  carry-forward rule and errors when two banks carry different base directories; `allow_mixed`
  enforcement matches Python; slicing, trimming, and renumbering are ported. `MediaBaseDir` is an
  RAII type whose `Drop` removes a directory the bank created, and leaves a caller-supplied
  directory alone. Bank equality is order-independent, matching `ItemBank.__eq__`; `iter_ordered()`
  exposes insertion order for callers that need it, since `item_number` derives from it.
- Evidence or review, when useful: lifetime tests cover created-and-dropped, caller-supplied, and
  merged-then-dropped.
- Obvious follow-ons: none.

### Work package: WP-B1 media asset layer

- Owner: `expert_coder`.
- Touch points: `qti-core/src/media/{mod.rs, resolve.rs, naming.rs, rewrite.rs, policy.rs, package.rs}`.
- Depends on: WP-A1; WP-F3 (HTML crate).
- Acceptance criteria: the media contract implemented in full. `MediaAsset`, `AssetKind`,
  `MediaPolicy` (4-variant enum), `MediaWarning` (with `resolved` and `action`),
  `MediaPolicyDecision`, and `MediaError`; `classify_src`, `guess_mime_type`, `scan_html_for_assets`,
  `resolve_local_path` with the traversal guard, `resolve_asset`, `compute_content_hash`,
  `assign_output_names`, `rewrite_html_srcs`, `rewrite_field_value`, `rewrite_item_media`,
  `placeholder_text`, and `apply_media_policy`.
  Permanent tests, all inline, chosen for behaviors that could realistically regress: every source
  kind classifies correctly, including absolute paths and protocol-relative URLs; traversal escape
  rejected; unsupported extension rejected by name; missing file rejected with item CRC and resolved
  path in the message; the three collision and dedup cases; the four policies against the three
  source kinds; every diagnostic carrying all five provenance fields.

  **HTML rewrite, permanent subset.** Five cases, each a distinct bug class rather than a syntax
  variant, each asserting content outside `<img src>` survives byte-identical: mixed quoting
  (single, double, unquoted) in one fragment; uppercase `<IMG SRC=>`; a `data-src` pseudo-attribute
  left untouched; an `<img` string inside a `<script>` block; and a malformed unclosed tag.
  The wider syntax sweep (entities adjacent to the tag, nested markup, table cells, self-closing
  forms, query strings, multiple images per field) is the decision rule for WP-F3's crate selection,
  where it does real work once. Promoting one of those cases to a permanent test happens if and when
  it catches something the five do not.
- Evidence or review, when useful: `architect` confirms the writer-side and reader-side helpers sit
  in separate modules over the shared core.
- Obvious follow-ons: none.

### Work package: WP-B2 zip writer

- Owner: `coder`.
- Touch points: `qti-core/src/zip.rs`.
- Depends on: WP-A0.
- Acceptance criteria: `ArchiveMap = BTreeMap<String, ArchiveEntry>` where `ArchiveEntry` is
  `Bytes(Vec<u8>)` or `SourcePath(PathBuf)`; `build_zip` writes entries in sorted order and emits
  explicit zero-byte directory markers for `empty_dirs`, keeping a real file entry when one exists
  at the same path. `collect_directory` is ported for reader-side use; writers build the map in
  memory. Tests cover filenames containing spaces and nested directories.
- Obvious follow-ons: none.

### Work package: WP-B3 IMS manifest

- Owner: `coder`.
- Touch points: `qti-core/src/manifest.rs`.
- Depends on: WP-B1; WP-F3 (XML crate).
- Acceptance criteria: `generate_manifest` produces QTI 1.2 and 2.1 manifests with the correct
  namespaces, metadata section, resource entries, `webcontent` resources for packaged media, and
  `<dependency identifierref>` links; identifiers are XML-name-safe. Output parses, and a local
  self-consistency test confirms every emitted reference names an emitted target. The oracle
  validates real packages from M7 onward.
- Obvious follow-ons: none.

### Work package: WP-B4 package integrity oracle

- Owner: `expert_coder`.
- Touch points: `crates/qti-integrity/`, `xtask/src/oracle_crosscheck.rs`.
- Depends on: WP-F3 (XML crate).
- Acceptance criteria: `check_package(path) -> Vec<Violation>` accepting a ZIP or an extracted tree,
  dispatching on package shape. All Python checks ported: manifest resolution, QTI 1.2 `varequal`
  and QTI 2.1 `correctResponse` answer linkage, rewritten `<img src>` resolution, raster dimension
  probing, identifier safety, QTI 2.1 outcome declarations, and every `blackboard_export_zip`
  cross-reference. Plus the new media trace check described in M6. Plus M6's four automated exit
  criteria. Each check carries a provenance annotation naming the LMS failure or format requirement
  it derives from, or marking it as advisory.
  The negative corpus is generated in code from the format specifications, so it stays inline and
  cannot drift out of existence.
- Evidence or review, when useful: `reviewer` audits independently, with the negative corpus as the
  audit's main artifact.
- Obvious follow-ons: expose it as `qti-package-maker check <path>` in WP-F2; publish the provenance
  annotations as `docs/PARITY.md`.

### Work package: WP-G0 engine traits and three probe engines

- Owner: `architect` (design and reader survey), `expert_coder` (implementation).
- Touch points: `qti-engines/src/{lib.rs, traits.rs, human_readable/, canvas_qti_v1_2/, bbq_text_upload/}`.
- Depends on: WP-A4, WP-B1, WP-B2, WP-B3, WP-B4.
- Acceptance criteria: the object-safe `Writer` and `Reader` traits from the architecture section,
  the generic `render_bank` loop with its `RenderHooks`, and `EngineError` are implemented, and a
  populated registry slice holds all three probes as trait objects. `ReadOutcome` carries whatever
  the reader survey finds all four Python readers need, including partial success with collected,
  located warnings. All three probes are complete engines, and `bbq_text_upload` round-trips by
  `ItemFingerprint`.
  Build the registry-holds-trait-objects step first and confirm it compiles before writing either
  writer; that ordering surfaces an object-safety problem in an hour rather than at M12.
- Evidence or review, when useful: three maximally dissimilar probes plus a survey covering the
  three readers no probe exercises, so the trait meets every shape before eight packages depend on it.
- Obvious follow-ons: dispatch M8, M9, and M11 concurrently on sign-off.

### Work packages: WP-C2..WP-C6 text-format engines (M8)

| WP | Engine | Direction | Notes |
| --- | --- | --- | --- |
| WP-C2 | `text2qti` | read + write | Markdown-ish. Python raises `NotImplementedError` on MATCH, MULTI_FIB, ORDER; the port returns `UnsupportedItemKind`. The reader parses per-choice feedback lines and discards them, matching Python. |
| WP-C3 | `okla_chrst_bqgen` | read + write | BQGen format; unrecognized fields pass through untouched. |
| WP-C4 | `moodle_aiken` | write | Aiken format; MC only; refuses RDKit-bearing items with a typed error. Placeholder media policy. |
| WP-C6 | `exam_yaml` | write | Serializes via `serde` on the WP-A1 model; uses the WP-F3 YAML crate. |

(`bbq_text_upload` and `human_readable` are delivered complete by WP-G0 as trait probes.)

- Owner: `coder`, one fresh subagent each.
- Touch points: `qti-engines/src/<engine>/` plus `tests/engine_<name>.rs`.
- Depends on: WP-G0; WP-B1.
- Acceptance criteria (each): every item kind the Python engine supports produces output;
  unsupported kinds return a typed error naming the kind and engine; the engine's row of the media
  table is verified end to end; read+write engines round-trip to an identical `ItemFingerprint` set.
- Obvious follow-ons: report the constructor signature to WP-F1.

### Work package: WP-D2 Blackboard QTI 2.1 writer (M9)

- Owner: `expert_coder`.
- Touch points: `qti-engines/src/blackboard_qti_v2_1/`.
- Depends on: WP-G0; WP-B1, WP-B2, WP-B3, WP-B4.
- Acceptance criteria: QTI 2.1 items plus assessment metadata, per-item files, packaged media; an
  MC+MA+MATCH+NUM+FIB bank with one embedded image produces a ZIP passing `qti-integrity` clean
  including the media trace; a `data:` URI produces a typed error before any output is written;
  every `correctResponse` names a choice identifier declared in the same item, derived from list
  position as Python does; the collision cases associate each image with its own item.
- Obvious follow-ons: report the constructor signature to WP-F1.

### Work package: WP-D3 Blackboard pool-export writer (M9)

- Owner: `expert_coder`.
- Touch points: `qti-engines/src/blackboard_export_zip/write/`.
- Depends on: WP-G0; WP-B1, WP-B2, WP-B3, WP-B4.
- Acceptance criteria: produces the `.dat` pool, `imsmanifest.xml`, CSResourceLinks, csfiles
  binaries with LOM sidecars, and the `sanitize_question_html` whitespace-in-`<tr>` defusal that
  keeps the Ultra question-expand renderer working; the ZIP passes `qti-integrity` clean including
  every Blackboard cross-reference and the media trace.
- Evidence or review, when useful: `reviewer` audits independently; this and M10 carry the plan's
  concentrated risk.
- Obvious follow-ons: report the constructor signature to WP-F1.

### Work packages: WP-D4a..WP-D4e Blackboard pool reader (M10)

Five deliverables, one source file each; see the M10 table for the mapping and each one's
independent verification.

- Owner: `expert_coder`.
- Touch points: `qti-engines/src/blackboard_export_zip/read/<file>.rs` plus that file's test module.
- Depends on: WP-D3; WP-D4b through WP-D4e additionally depend on WP-D4a for the type-registration
  table.
- Acceptance criteria: each sub-work-package's row, plus these behaviors spread across them --
  `mat_formattedtext` recovery reverses the write path's single escape; an unparseable item or
  unrecognized `bbmd_questiontype` is skipped with a warning naming its source while the read
  succeeds; a missing or empty manifest pool entry produces a typed error; recovered images land in
  the bank-owned extraction directory under collision-safe plain filenames with item HTML rewritten
  to match, so an imported bank flows through the same `collect_assets()` path as file-authored
  input.
- Evidence or review, when useful: `reviewer` audits the milestone; the round-trip assertion is the
  milestone's exit criterion rather than any single package's.
- Obvious follow-ons: report the constructor signature to WP-F1.

### Work package: WP-E1 HTML self-test engine (M11)

- Owner: `coder`.
- Touch points: `qti-engines/src/html_selftest/`.
- Depends on: WP-G0; WP-B1.
- Acceptance criteria: renders one randomly selected item to a single self-contained HTML file with
  inline CSS, inline JavaScript grading, and every local image inlined as a base64 `data:` URI;
  supports all seven item kinds; the MkDocs Material light/dark CSS variable mapping is preserved;
  every `src` and `href` in the output is a `data:` URI or a document-internal reference.
- Obvious follow-ons: report the constructor signature to WP-F1.

### Work package: WP-F1 engine registry (M12)

- Owner: `coder`.
- Touch points: `qti-engines/src/registry.rs`.
- Depends on: WP-C2..C6, WP-D2, WP-D3, WP-D4a..e, WP-E1, WP-G0.
- Acceptance criteria: a `const ENGINES: &[EngineEntry]` slice where each entry carries `name`,
  `media_policy`, `make_writer: Option<fn>`, and `make_reader: Option<fn>`; `can_read`/`can_write`
  are `is_some()`; name resolution implements exact-then-unique-prefix with an ambiguity error
  listing candidates. Every engine compiles unconditionally; a test asserts each appears once.
- Obvious follow-ons: an engine-capability table printer replacing `print_engine_table`.

### Work package: WP-F2 CLI binaries (M12)

- Owner: `coder`.
- Touch points: `crates/qti-cli/`.
- Depends on: WP-F1.
- Acceptance criteria: `bbq-converter` accepts `-i/--input`, `-o/--output`, `-n/--limit`,
  `-q/--quiet`, `-v/--verbose`, `--allow-mixed`, `-f/--format` (repeatable), `-a/--all`, and every
  per-format shortcut (`-1 --qti12`, `-2 --qti21`, `-r --human`, `-b --bbq`, `-s --selftest`,
  `-A --aiken`, `-B --bbexport`); `clap` rejects `-o` combined with multiple formats; the
  `bbq-<name>-questions.txt` filename convention is honored; output-file naming
  (`qti12-<name>.zip`, `selftest-<name>.html`) is preserved exactly. `qti-package-maker` exposes
  `engines`, `item-types`, and `check <path>` subcommands.
- Evidence or review, when useful: an integration test asserts exit status and stderr text for three
  failure modes (missing input, unknown engine, unsupported item kind for the chosen engine).
- Obvious follow-ons: shell completions via `clap_complete`.

### Work package: WP-F4 differential parity harness (M13)

- Owner: `tester`.
- Touch points: `xtask/src/parity.rs`, `tests/corpus/`.
- Depends on: WP-F2.
- Acceptance criteria: `cargo xtask parity` runs a corpus of BBQ input files through both the
  installed Python `bbq_converter.py` and the Rust `bbq-converter`, then compares each format by the
  strongest practical semantic method:

| Format | Comparison method |
| --- | --- |
| `bbq_text_upload`, `text2qti`, `okla_chrst_bqgen` | Read both outputs back; compare `ItemFingerprint` sets, plus bank order |
| `blackboard_export_zip` | Read both back through the M10 reader; compare fingerprint sets; both ZIPs pass `qti-integrity` clean |
| `canvas_qti_v1_2`, `blackboard_qti_v2_1` | Both pass `qti-integrity` clean, then compare a normalized item projection parsed from the XML: per item, the question text, ordered choice texts, and correct-answer texts with each identifier dereferenced to its choice, so position-derived identifiers compare by meaning |
| `exam_yaml` | Parse both documents and compare the structures; the cheapest strong comparison available, covering every field |
| `moodle_aiken` | Parse both back with a small harness parser (stem, lettered choices, `ANSWER:` line) and compare question, choices, and correct answer |
| `human_readable` | Normalize whitespace and compare text; report the diff verbatim on mismatch |
| `html_selftest` | Extract the embedded answer data and choice texts from the generated JavaScript and compare those; the harness feeds a single-item bank so the engine's random selection is pinned |

  Corpus coverage, decided and enumerated so image behavior is measured rather than assumed: banks
  containing duplicate basenames in different directories; the same image referenced by many
  questions; multiple images in one question; filenames with spaces and mixed case; nested media
  directories; an external URL; a `data:` URI; an SVG; and a question with no image at all.
  Error-path inputs (missing file, unsupported extension, corrupt header, single-pixel image) live
  in the permanent `cargo test` suite where their typed errors are asserted directly, since a
  harness that must fail on both sides adds noise without adding signal.
  A divergence prints the engine, the item CRC, the differing field, and both values, and is
  escalated per the parity-authority order.
- Evidence or review, when useful: the harness is the operational definition of semantic parity. Its
  valid corpus is the same one M6 used to cross-validate the oracle, so the oracle was proven on
  those inputs before judging Rust output.
- Obvious follow-ons: run it in CI once M14 lands, on runners where the Python package installs.

### Work package: WP-G1 documentation port (M14)

- Owner: `maintainer`.
- Touch points: `docs/`.
- Depends on: M13.
- Acceptance criteria: `README.md` (first paragraph under 250 characters, pure prose, per house
  style), `docs/INSTALL.md`, `docs/USAGE.md`, `docs/CODE_ARCHITECTURE.md`, `docs/FILE_STRUCTURE.md`,
  `docs/ENGINES.md`, `docs/ENGINE_AUTHORING.md` (carrying the `template_class` worked example),
  `docs/FORMATS.md`, `docs/QUESTION_TYPES.md`, `docs/MEDIA.md` (the media contract, so it outlives
  this plan), `docs/PARITY.md` (the parity-authority order plus the per-check provenance table),
  `docs/DEPENDENCY_DECISIONS.md`, `docs/RELATED_PROJECTS.md` (naming the Python repo as upstream),
  `docs/ROADMAP.md`, and `docs/CHANGELOG.md`. Markdown links resolve and content is ASCII.
  The three-tier test classification goes in `tests/TESTS_README.md`, matching where the Python repo
  keeps it, rather than becoming a separate `docs/` file.
  Each of these documents a durable contract someone will need later: what images do, what parity
  means, why each dependency was chosen, what the architecture is, and how to run it. Execution
  evidence stays out of `docs/`.
- Obvious follow-ons: none; this closes the documentation set.

### Work package: WP-G2 CI and release lane (M14)

- Owner: `maintainer`.
- Touch points: `.github/workflows/`, workspace `Cargo.toml` metadata, `VERSION`.
- Depends on: M13.
- Acceptance criteria: CI runs `cargo fmt --check`, `cargo clippy -- -D warnings`, and `cargo test`
  on macOS and Linux, plus `cargo xtask parity` and `cargo xtask oracle-crosscheck` on runners where
  the Python package installs; `cargo build --release` produces a binary on both platforms; crate
  metadata carries the LGPLv3 license, repository URL, and a CalVer version synchronized with
  `VERSION`.
- Obvious follow-ons: reuse the propagated `devel/make_release.py` for GitHub source releases.

## Acceptance criteria and gates

Gates come in two kinds, and progress reporting names which kind passed.

**Automated gates** (a command exits zero):

- **Per-patch:** `cargo fmt --check`, `cargo check`, the package's own `cargo test`, and
  `cargo clippy -- -D warnings` before a work package reports done.
- **Per-milestone:** each milestone's automated exit criteria.
- **Oracle agreement (M6):** `cargo xtask oracle-crosscheck` reports identical violation lists on
  both the valid and negative corpora.
- **Integration (M13):** full workspace `cargo test`; every ZIP passes `qti-integrity`; all four
  readers round-trip by `ItemFingerprint` with order checked where formats preserve it;
  `cargo xtask parity` reports zero divergences under the per-format table.

**Subagent review gates** (a named agent judges and records a decision):

- **M2:** `architect` signs off on the item enum shape; the CRC sweep result is recorded.
- **M4:** `architect` confirms the media layer's writer/reader module separation.
- **M6:** `reviewer` audits the oracle for producer-derived reimplementation; provenance annotations
  are recorded.
- **M7:** `architect` signs off on the trait shape, having completed and recorded the reader survey.
- **M9, M10:** `reviewer` audits WP-D3 and the M10 reader independently of their implementers.

Both kinds run unattended. The distinction keeps progress reporting accurate: a milestone that has
passed its commands but not its review is not complete, and saying so plainly is the point.

## Test and verification strategy

Four tiers, in increasing cost, with each check's permanent home given in `## Test classification`:

1. **Unit tests, in-crate.** Pure-function correctness with inline inputs, including every
   fingerprint sensitivity case and the five-case HTML rewrite subset.
2. **Round-trip invariants by `ItemFingerprint`.** For the four readable engines: build a bank in
   code, write, read, assert an identical fingerprint set, and assert order for formats that
   preserve it. Fingerprint rather than CRC, because the CRC omits `answer_text` and `answers_list`
   and would pass a reader that corrupted every correct answer. Set rather than sequence for the
   fingerprints, because `ItemBank.__eq__` is order-independent by design; order is a separate
   explicit assertion so an ordering regression stays visible.
3. **Integrity checks.** Every ZIP-producing engine builds a representative bank with images and
   must pass `qti-integrity` clean, including the media trace. The regression canaries and the
   generated negative corpus must still detect their bug classes.
4. **Differential parity.** Python and Rust run the same corpus; every format is compared by the
   method in WP-F4's table; divergences escalate per the parity-authority order.

Tier 3's independence deserves stating plainly: a checker rewritten alongside the producer it checks
can develop a matching blind spot, and agreeing on valid packages alone would not reveal it. M6
therefore requires agreement on independently constructed defects as well.

## External validation

Real LMS imports are the only true ground truth, and they require a person with sandbox credentials.
They are **external release validation**, not an implementation completion dependency. Every
milestone's exit criteria, every gate, and every work package's acceptance criteria run unattended;
M14 closes on automated and subagent-review criteria alone.

The automated substitute is `qti-integrity`, which encodes what two real Blackboard import failures
already taught the Python repo, plus the new media trace check that follows each image from item
HTML to a real ZIP entry. It is a proxy: its provenance-backed checks sit at tier 2 of the parity
authority, below observed LMS behavior, and its advisory checks sit at tier 4.

When sandbox access is available these imports are worth doing, and their results belong in
`docs/MEDIA_LMS_PROBES.md` alongside the Python repo's existing probe records. A failure found this
way is tier-1 evidence and opens a follow-up plan.

- One Rust-produced Canvas QTI 1.2 package into Canvas.
- One Rust-produced Blackboard pool-export ZIP into Blackboard Original.
- One Rust-produced QTI 2.1 package into Blackboard Ultra.

## Migration and compatibility policy

- The Python repository keeps running, unmodified, alongside the Rust port.
- CLI compatibility is a hard requirement: `bbq-converter` accepts the same flags and the same
  `bbq-<name>-questions.txt` input convention, so a user swaps the binary and everything else stays.
- Output-file naming is preserved exactly.
- Downstream Python callers (`biology-problems`/`bptools`) keep importing the Python package until
  the PyO3 crate ships; see `## Roadmap context` for why the port succeeds meanwhile.
- The API constraint that keeps that crate additive: owned values in and out, no lifetimes in public
  signatures, no `&dyn Trait` in return position on the top-level API.

## Roadmap context

Work this plan places out of scope, each with the reason this version succeeds without it. All of it
lands in the new repo's `docs/ROADMAP.md` at WP-G1.

- **PyO3 bindings.** Succeeds without: the Python package keeps serving Python callers unchanged,
  so nothing downstream breaks while the Rust CLI serves the command-line use directly. The
  owned-value API constraint is what keeps this additive later.
- **Stable choice identifiers.** Succeeds without: both Python and this port derive identifiers from
  list position at render time, and every LMS output is self-consistent within an item, which is
  what the identifiers exist to guarantee. Stability becomes necessary only when per-choice feedback
  arrives.
- **Hints and per-item feedback.** Succeeds without: no engine reads a feedback field today, so
  carrying one would add serialization surface with no user-visible effect.
- **Content-addressed media dedup.** Succeeds without: dedup by `src` matches Python exactly and
  already collapses the common case of one image referenced by many questions. Two distinct paths
  holding identical bytes produce two entries, costing a few kilobytes and nothing else.
- **Byte-identical XML output.** Succeeds without: LMS importers read structure, and
  `qti-integrity`'s trace and linkage checks verify structure directly. Matching one library's
  pretty-printer would bind the port to that library permanently.
- **Reader auto-detection, seeded shuffle, per-engine feature gates, remote image fetching.**
  Succeeds without: explicit engine selection is what the CLI does today, the harness pins random
  selection with a single-item bank, every engine compiling is what Python does, and remote images
  are kept verbatim with a warning as Python does. Each is additive once the registry and media
  boundary exist.

## Risk register

| Risk | Impact | Trigger | Owner | Mitigation |
| --- | --- | --- | --- | --- |
| Trait design changes after fan-out | High: rework across 8 concurrent packages | An engine or one of the four readers cannot express itself through the traits | `architect` | M7 is its own milestone, proves three dissimilar shapes including a reader, and surveys all four Python readers before sign-off |
| Registry cannot hold its engines | High: discovered at M12, invalidating the M7 sign-off | A trait with an associated type used as `Box<dyn Writer>` | `architect` | The decided shape keeps associated types below the object-safe boundary; M7 compiles the populated registry as its first step, before either probe writer |
| Oracle and producer share a blind spot | High: a real bug passes both | A Rust check derived from producer assumptions, or both omitting a check | `expert_coder` | M6 requires agreement on a valid corpus with zero Rust output *and* on an independently constructed negative corpus covering every check category |
| Round-trip invariant too weak | High: a corrupted correct answer passes CI | CRC-set equality used as the invariant | `tester` | `ItemFingerprint` replaces it; a test asserts equal CRCs with unequal fingerprints |
| Fingerprint too strict on media | High: M10 fails on every correct run | Media compared by `src` spelling | `expert_coder` | Media compares by content hash plus placement; the expected-rewrite table names all six legitimate transformations |
| An image associates with the wrong item | High: a student sees the wrong figure | Basename collision across directories | `expert_coder` | Sorted-by-`src` deterministic naming; the three collision cases are permanent tests and appear in the M13 corpus |
| A packaged image an LMS cannot load | High: silent breakage in the field | Manifest and ZIP entry disagree | `expert_coder` | The M6 media trace check follows every image from item HTML through the manifest to a real ZIP entry |
| Ordering regression hidden by set comparison | Medium: item numbering silently changes | Only fingerprint sets compared | `tester` | Order is a separate explicit assertion for formats that preserve it |
| The checker becomes a specification | Medium: an advisory check overrules real Python behavior | A tier-2 claim for a check with no traceable origin | `architect` | Tier 2 requires recorded provenance; advisory checks sit at tier 4 |
| CRC disagreement with Python | Medium: bank keying and dedup diverge | `cargo xtask crc-corpus` reports a mismatch | `expert_coder` | Full corpus run in M2; XMODEM parameters are unambiguous, so a mismatch points at encoding |
| Item model changes after M3 | High: every engine matches on it | A writer needs a field the enum lacks | `architect` | Sign-off is an M2 exit criterion; the model carries no speculative fields |
| Pool reader underestimated | High: largest single unit in the port | M10 slips or stalls opaquely | `expert_coder` | Five sub-deliverables, one source file each, each independently verifiable; independent `reviewer` audit |
| HTML rewrite alters surrounding markup | Medium: real question HTML silently mangled | The syntax sweep fails during crate selection | `coder` | WP-F3 chooses the crate on that sweep before M4 starts; five representative cases become permanent tests |
| Test suite accumulates fragile checks | Medium: the fast lane decays and gets skipped | A one-time proof lands as a permanent test | `maintainer` | `## Test classification` assigns every check a home; cross-language checks live in `xtask`, and the CRC sweep retires after M2 |
| A divergence gets resolved locally | Medium: two workstreams fight over one behavior | A coder judges Python behavior wrong | `architect` | The parity-authority order and its standing rule; divergences are reported with both values |
| Scope creep into roadmap features | Medium: milestones slip | A subagent adds stable choice IDs because Rust makes them easy | `architect` | `## Roadmap context` gives each deferral its reason; the design philosophy states the rule |

## Rollout and release checklist

- [ ] M2: `cargo xtask crc-corpus` full agreement recorded; the one-time sweep retired.
- [ ] M4: media contract table verified cell by cell; `architect` module-separation sign-off recorded.
- [ ] M6: `cargo xtask oracle-crosscheck` agreement on both corpora recorded; provenance table written.
- [ ] M7: trait sign-off recorded, including the four-reader survey findings.
- [ ] M13: integration gate green; `cargo xtask parity` reports zero divergences per format.
- [ ] `docs/CHANGELOG.md` carries the port entry with its decisions and failures.
- [ ] `docs/MEDIA.md` and `docs/PARITY.md` published; test tiers documented in `tests/TESTS_README.md`.
- [ ] Release binaries built for macOS (aarch64) and Linux (x86_64).
- [ ] `docs/RELATED_PROJECTS.md` in both repos cross-links Python and Rust.
- [ ] External validation scheduled; results land in `docs/MEDIA_LMS_PROBES.md` when sandbox access
      allows, on its own timeline.

## Documentation close-out requirements

Two records, with a clean split: transient execution evidence lives in the progress tracker only,
and `docs/` carries durable decisions. Keeping plan maintenance from becoming its own workstream is
the point.

- **`refactor_progress.md` (transient).** One line per milestone: which automated gates passed,
  which review gates passed, and the date. Gate-by-gate evidence lives here and nowhere else.
- **`docs/CHANGELOG.md` (durable).** One entry per milestone at completion, plus a
  `### Decisions and Failures` record of the decisions a future maintainer would otherwise have to
  rediscover: the object-safe trait boundary with the generic render loop beneath it, compile-time
  registry over runtime discovery, in-memory archive map replacing staging directories, RAII media
  directory, `ItemFingerprint` over CRC equality, media compared by content and placement,
  dedup keyed on `src`, choices as plain strings, no feedback field, the four M1 crate choices, the
  minimum-size check recorded as advisory, and each parity divergence `architect` resolved.
- Archive / closure notes: on M14 completion, `git mv` the active plan to `docs/archive/`.

## Patch plan and reporting format

One patch per work package, grouped by milestone.

- M1: patch 1 (WP-A0), patch 2 (WP-F3) -- concurrent.
- M2: patch 3 (WP-A1), patch 4 (WP-A2) -- concurrent.
- M3: patch 5 (WP-A3), patch 6 (WP-A4) -- serial.
- M4: patch 7 (WP-B1).
- M5: patch 8 (WP-B2), patch 9 (WP-B3) -- concurrent.
- M6: patch 10 (WP-B4) -- concurrent with M2-M5.
- M7: patch 11 (WP-G0) -- serial bottleneck.
- M8: patches 12-15 (WP-C2, C3, C4, C6) -- four concurrent.
- M9: patches 16-17 (WP-D2, WP-D3) -- concurrent with M8 and M11.
- M10: patch 18 (WP-D4a), then patches 19-22 (WP-D4b, D4c, D4d, D4e) -- four concurrent.
- M11: patch 23 (WP-E1) -- concurrent with M8 and M9.
- M12: patch 24 (WP-F1), patch 25 (WP-F2) -- serial.
- M13: patch 26 (WP-F4) plus the integration gate run.
- M14: patch 27 (WP-G1), patch 28 (WP-G2) -- concurrent.

Each patch reports: work-package ID, owning milestone, files touched, the Cargo commands run with
their results, which gates passed and of which kind, and any parity divergence observed with both
values.

## Resolved decisions

Every question this plan raised is decided. Nothing is left for a later reader to settle.

- **Repository name: `qti-package-maker-rs`**, a four-crate workspace plus `xtask`.
- **The object-safe boundary is `save_package` / `read_items`, not per-item render.** `Writer` and
  `Reader` carry no associated types, so the registry holds them as trait objects; the generic
  `render_bank<R>` loop sits below, letting each engine keep its own rendered representation.
- **M5 proves manifest construction with its own local self-consistency check**; the cross-validated
  oracle applies from M7 onward, so M5 and M6 stay genuinely concurrent.
- **M2 owns fingerprint comparison over `MediaRef`; M4 owns media resolution.** M2 stays
  filesystem-free, and the milestone graph matches the design.
- **The minimum-visible-size check is advisory (tier 4); the unreadable-header check is structural
  (tier 2).** Small valid images such as icons stay legitimate content.
- **Permanent tests cover regression-prone behavior**: resolution and rewrite correctness, collision
  association, missing media, package reference integrity, and Blackboard recovery. Exhaustive
  syntax sweeps do their work once, as crate-selection decision rules.
- **Execution evidence lives in `refactor_progress.md`; `docs/` carries durable contracts only.**
- **Python interop: pure Rust in this plan.** The API constraint keeps a PyO3 crate additive; see
  `## Roadmap context` for why the port succeeds without it now.
- **All ten engines are in scope**, spread across five milestones so each group has its own exit
  criteria and visible progress.
- **Parity bar: semantic, with a named four-tier authority.** Tier 2 requires recorded provenance,
  so a check cannot become a specification merely by existing.
- **`ItemFingerprint`, not CRC equality, is the round-trip invariant.**
- **Image sameness is content hash plus placement.** Filename, `src`, path, output name, and pixel
  dimensions are excluded, because each varies legitimately across a correct round trip.
- **All six platform `src` rewrites are expected transformations** and pass parity.
- **Every engine-by-source-kind cell is defined** in the media contract table.
- **Output naming is keyed on `src`, assigned in sorted `src` order**, so collisions resolve
  deterministically and an image never associates with the wrong item.
- **Dedup is by `src`**: many references to one `src` produce one package entry; two distinct `src`
  values produce two entries even with identical bytes.
- **One failing image rejects the bank before any output is written**, naming the item and the `src`.
- **Media diagnostics carry five fields**: engine, item CRC, original `src`, resolved target, action.
- **The dimension check guards against tracking-pixel-sized and unreadable rasters**; vector images
  take the packaged-with-a-warning path; large images are valid.
- **Writers and readers share classify, resolve, hash, and rewrite**, with each direction's
  specialization in its own module.
- **Fingerprint comparison is set-based, with order asserted separately**, matching
  `ItemBank.__eq__`.
- **The oracle is cross-validated on valid and corrupted corpora before it is trusted**, and gains a
  media trace check from item HTML through the manifest to a real ZIP entry.
- **Choices are plain strings**; identifiers derive from list position at render time.
- **The model carries no feedback field.**
- **Every engine compiles unconditionally.**
- **Peripherals stay in Python**, keeping scientific-color libraries out of the Rust tree.
- **The registry is an explicit list**, greppable in one file.
- **Packages are assembled in memory** through `ArchiveMap`.
- **Every check has one home**: permanent `cargo test`, `cargo xtask` tooling, or a one-time proof
  that retires after recording its result.
- **One committed binary fixture** (`bb_export_slice.zip`); every other input is built in code.
- **No throughput, latency, or size gate exists**, because no such requirement exists for a batch
  converter and an invented number would gate the work on nothing.
- **`html_selftest` random selection is pinned in the harness by feeding a single-item bank**, which
  keeps the engine's behavior identical to Python.
- **Real LMS imports are external release validation.**

Decision owner during execution: `architect` for the item enum at M2, the media module separation at
M4, the trait shape and reader survey at M7, and every parity divergence escalated during M8-M13,
applying the parity-authority order and recording each outcome in `docs/CHANGELOG.md`.
