# Do AI agents benefit from writing tests?

This is a selected 20-issue SymPy pilot of two questions:

1. Does requiring a new behavioral regression test improve immediate issue resolution?
2. Do generated suites detect the original bug and prevalidated mutations after the fix?

The model is **GPT-6 Astra**, medium reasoning, accessed through **Codex CLI authenticated with ChatGPT**. The subscription's capacity is consumed. No API key, other provider, API dollar conversion, or extra inference purchase is used.

The website is `unit-testing.html`. It loads measured artifacts from `assets/experiments/unit-testing/`. The chart is exported with Matplotlib as PNG and SVG; the tweet is a draft, never automatically posted. An incomplete batch stays labeled incomplete.

## Protocol

Read `protocol.json` before running. Twenty historical SymPy issues from SWE-bench Verified, two policies, two repetitions: 80 scheduled attempts. Existing tests are allowed in both arms. The new-test arm must add and execute `test_agent_regression.py`. Both get five minutes including test writing. A seeded schedule and task selection are frozen before scored inference.

This is a **local adaptation**, not an official SWE-bench score or a replication of the paper's exact scaffold. It uses local macOS, Python 3.9, and pytest, not mini-SWE-agent and the official Docker harness. Public benchmark contamination, single-repository selection, small sample size, and the short cap limit interpretation.

The original paper and replication package:

- https://arxiv.org/html/2602.07900v2
- https://doi.org/10.5281/zenodo.19251470
- https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified

## Prepare a separate local data directory

Requirements: macOS with `sandbox-exec`, Python 3.9, Python 3.11+ for the runner, Git, Node-free site preview, Codex CLI supporting `--ignore-user-config`, and `uv`. The plotting interpreter needs Matplotlib. The tested Codex version and Python version are saved in the manifest.

```sh
mkdir -p docs/preview/unit-testing
uv venv --python /usr/bin/python3 docs/preview/unit-testing/venv
uv pip install --python docs/preview/unit-testing/venv/bin/python -r experiments/unit-testing/requirements.txt
python3 experiments/unit-testing/download.py --data docs/preview/unit-testing
python3 experiments/unit-testing/bench.py prepare --data docs/preview/unit-testing
codex login status
python3 experiments/unit-testing/bench.py run --data docs/preview/unit-testing --limit 1
python3 experiments/unit-testing/bench.py run --data docs/preview/unit-testing
python3 experiments/unit-testing/report.py --data docs/preview/unit-testing
```

The data directory is ignored by Git. Never put credentials in it. Login remains in the normal CLI credential store. API-key variables are omitted from the child process environment and ChatGPT login is required. No credentials are copied into trial repositories or published artifacts.

Every task receives a clean archive of its recorded base commit and a new one-commit Git repository. Withheld test patches, reference fixes, mutations, grader source, and other runs are denied to the trial process by an outer macOS sandbox. Codex's inner sandbox is disabled because macOS Seatbelt profiles cannot nest. The outer profile also forbids writes to the website. Internet prohibition and instruction compliance require trajectory audit; this is not a hermetic network sandbox.

## Environment validity and scoring

Before selection, each original must fail at least one official FAIL_TO_PASS check, pass every PASS_TO_PASS check, and the reference patch must pass all of them. Names duplicated across test-patch files are mapped to all matching top-level functions. Exclusions are retained. This deliberately favors cases whose local environments and graders work; it is not a random sample of all SWE-bench tasks.

Grading applies only production Python changes to a new base, then the official test patch. Agent edits to existing tests or infrastructure never enter the acceptance grader. Skips, errors, and missing collection are not passes. A timed-out agent can still leave a correct patch; timeout status remains visible alongside patch correctness. Infrastructure failures are not relabeled as incorrect patches.

Generated tests are evaluated on the agent patch, reference patch, original base, and reference-derived mutations. A reference incompatibility is not automatically a bad test: one observed suite exposes an empty-tuple regression in the benchmark reference fix itself, documented separately in public findings.json. The frozen validity rule is retained without outcome-based adjustment. A suite must pass on the reference before contributing to original-bug detection and mutation scores. Test-case failures, including behavioral exceptions, count as detections; collection errors and skipped tests do not. Tests targeting internal implementation details may fail on a different correct patch and are reported as invalid for reference-based scoring.

Mutation operators replace comparisons, booleans, arithmetic operators, and small integers on reference-added lines. Up to 20 candidates are considered per issue; at most three are retained if syntax-valid and detected by the official FAIL_TO_PASS checks. Some issues have no eligible mutants. Mutant survival does not establish equivalence.

A conservative automated audit inspects all recorded command strings and file-change paths; ambiguous scripts require individual review. Automatic compliance flags inspect artifacts and execution commands. Review complete trajectories for inline checks, deleted tests, changes to existing tests, internet use, and forbidden reads before calling a run compliant. Put a `compliance_review` object with `compliant` and `note` into each private `result.json`; regenerate exports. Noncompliant runs stay in the assigned arm, with violations reported.

## Analysis and reproducibility

The main comparison is paired by issue and repetition. The final effect interval resamples entire issues, retaining both repetitions; an exact sign-flip test also operates at issue level. Partial runs do not receive final paired inference. A nonsignificant result is not evidence of equivalence. Token totals separate cached input from total input, and do not estimate subscription dollars.

In this completed pilot every task's paired difference was zero. The prespecified bootstrap therefore returns `[0, 0]`; this is a degenerate resampling result, not useful population uncertainty or evidence of equivalence. The raw output is retained in JSON and the chart labels the limitation explicitly.

The runner never retries scored outcomes. Authentication, quota, or inference infrastructure failure stops the batch. Completed runs are resumable; a `started.json` without a result requires review before continuing. Preserve interrupted artifacts. Run a new protocol version and data directory if changing the model, cap, prompts, or selection after scored inference.

Public exports contain only experiment-specific material. Review and redact local paths before publishing trajectories. Keep the GitHub Pages preview unpublished until the website owner approves release.

After all 80 attempts and their policy reviews are complete:

```sh
python3 experiments/unit-testing/report.py --data docs/preview/unit-testing
python3 experiments/unit-testing/verify_results.py --data docs/preview/unit-testing
python3 experiments/unit-testing/bundle.py --data docs/preview/unit-testing
```

The evidence ZIP includes prompts, patches, generated tests, full recorded trajectories, launch settings, grader logs and XML, preflight evidence, the frozen manifest, and file checksums. To check an extracted bundle without invoking a model, run `python3 experiments/unit-testing/verify_results.py --data data --public public` from its root. Regenerating scores requires downloading the recorded base commits and rebuilding the local grading environment; rerunning inference also consumes subscription capacity and will not necessarily produce identical outputs.
