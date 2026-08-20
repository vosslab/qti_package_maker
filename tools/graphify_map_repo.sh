#!/usr/bin/env bash

set -euo pipefail

MODEL="qwen2.5-coder:7b-instruct"
MODE="${1:-update}"

if [[ "$MODE" != "fresh" && "$MODE" != "update" && "$MODE" != "context" ]]; then
	echo "Usage: $0 [fresh|update|context]"
	echo "  fresh  - rebuild the Graphify graph from scratch"
	echo "  update - reuse existing graphify-out when available, then refresh labels/benchmarks"
	echo "  context - print AI-manager dispatch context only (no graphify work)"
	exit 1
fi

# Require execution from the Git repository root.
GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"

if [[ -z "$GIT_ROOT" ]]; then
	echo "Error: current directory is not inside a Git repository."
	exit 1
fi

if [[ "$PWD" != "$GIT_ROOT" ]]; then
	echo "Error: run this script from the repository root:"
	echo "  $GIT_ROOT"
	exit 1
fi

print_manager_context() {
cat <<'EOF'
GRAPHIFY CONTEXT (FOR MANAGERS)

What Graphify is:
- Graphify is a static code-map builder for this repository.
- It indexes files, symbols, imports, and call relationships into graphify-out/.
- It produces a dependency graph and community-aware view that helps managers scope work
  before opening source files.

What Graphify commands to use:
- graphify query "<question>" --budget 1500
  - Start with one high-level question to identify affected modules, symbols, and risk areas.
- graphify explain "<symbol_or_path>"
  - Read concise meaning, neighbors, and dependencies for a target.
- graphify affected "<symbol_or_path>" --depth 2
  - Expand precise impact area before assigning code changes.
- graphify path "<symbol A>" "<symbol B>"
  - Find dependency paths when a boundary decision depends on flow.
- graphify god-nodes --top 20
  - Identify high-connectivity symbols before choosing delegation boundaries.
- graphify label . --backend=ollama --model="qwen2.5-coder:7b-instruct"
  - Assign community labels after extract.
- graphify benchmark
  - Produce consistency output for current graph state.

How to orient subagents with fewer tokens:
1) Run one focused Graphify pass first.
2) Convert each query result into one narrow task slice (max ~1-3 high-impact symbols).
3) Dispatch subagents with only the needed Graphify evidence and required scope, not the full repo.
4) Require `graphify` evidence in the first message before deeper file reading.

Suggested manager dispatch template:
{
  "task": "<short task statement>",
  "scope_hint": "<expected impacted symbols/files>",
  "graphify_inputs": [
    "graphify-out/GRAPH_REPORT.md",
    "graphify query results",
    "graphify explain / affected outputs"
  ],
  "evidence_gate": [
    "Only edit files not listed in graphify risk map unless query/affected expands scope."
  ],
  "output": "<exact artifact + verification checklist>"
}

Goal:
Use Graphify to shrink each subagent prompt to only the minimum required symbols and
dependency context, which lowers prompt size and reduces token spend while keeping task
coverage stable.
EOF
}

if [[ "$MODE" == "context" ]]; then
	print_manager_context
	exit 0
fi

ollama pull $MODEL

echo "Building Graphify graph for: $(basename "$GIT_ROOT") ($MODE)"

GRAPHIFY_ARGS=(extract . --code-only)
DO_FULL_EXTRACT=0
if [[ "$MODE" == "fresh" ]]; then
	DO_FULL_EXTRACT=1
elif [[ "$MODE" == "update" ]] && [[ ! -d graphify-out || ! -f graphify-out/GRAPH_REPORT.md ]]; then
	echo "No prior graphify output found; performing a fresh run."
	DO_FULL_EXTRACT=1
else
	echo "Existing graphify output found; updating labels and benchmarks."
fi

# Include Cargo workspace information when present.
if [[ -f Cargo.toml ]]; then
	GRAPHIFY_ARGS+=(--cargo)
fi

if (( DO_FULL_EXTRACT )); then
	graphify "${GRAPHIFY_ARGS[@]}"
fi

echo
echo "Labeling Graphify communities with Ollama..."

graphify label . \
	--backend=ollama \
	--model="$MODEL"

echo
graphify benchmark

echo
echo "======================================================================"
echo "GRAPHIFY READY"
echo "======================================================================"
echo
cat <<'EOF'
Give the following instruction to the AI agent manager:

Review the Graphify analysis for this repository before planning or
delegating work. Use graphify-out/GRAPH_REPORT.md and Graphify queries to
understand relevant subsystems, dependencies, and likely impact areas.

Use Graphify to narrow repository context before reading source broadly.
For the current task, identify the relevant communities, files, symbols,
dependency paths, and affected code. Use that information to create
focused task boundaries for subagents. Give each subagent only the
repository context needed for its assigned work.

Useful commands include:
  graphify query "<task or architectural question>" --budget 1500
  graphify explain "<symbol>"
  graphify affected "<symbol>" --depth 2
  graphify path "<symbol A>" "<symbol B>"
  graphify god-nodes --top 20

Treat Graphify as an architectural index and use source code as the final
source of truth when implementation details need confirmation.
EOF

print_manager_context
