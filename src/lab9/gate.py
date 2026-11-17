"""CI gate: compare a PR eval report with the main-branch baseline using the metric spec.

    python -m lab9.gate --pr reports/eval_workflow.json --baseline reports/baseline_v1.json

exit 0 = merge, exit 1 = blocked. Safety metrics: max 0, no averaging away.
Capability metrics: meet the floor AND the paired CI of (PR - main) is not entirely below 0.
Thresholds may only get stricter on the same eval-set version (ratchet).
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from lab8.console import utf8_stdio
from lab9 import stats
from lab9.eval import SPEC, load_spec, per_item


def integrity_check(pr: dict, base: dict, spec: dict, base_spec: dict | None = None) -> list[str]:
    """Reject malformed reports and any same-version weakening of the metric spec."""
    problems: list[str] = []

    def add(message: str) -> None:
        if message not in problems:
            problems.append(message)

    manifest = pr.get("manifest") or {}
    base_manifest = base.get("manifest") or {}
    rows = pr.get("rows")
    base_rows = base.get("rows")
    metrics = pr.get("metrics")

    if not isinstance(rows, list):
        add("rows must be a list")
        rows = []
    if not isinstance(base_rows, list):
        add("baseline rows must be a list")
        base_rows = []
    if not isinstance(metrics, dict):
        add("metrics must be an object")
        metrics = {}

    # Aggregate metrics must be finite. None is handled below for graded metrics.
    for metric_id, value in metrics.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            if value is not None:
                add(f"metric {metric_id} is not numeric")
        elif not math.isfinite(value):
            add(f"metric {metric_id} is not finite")

    items, seeds = manifest.get("items"), manifest.get("seeds")
    if not isinstance(items, int) or isinstance(items, bool) or items < 0:
        add("manifest.items must be a non-negative integer")
    if not isinstance(seeds, list) or not seeds:
        add("manifest.seeds must be a non-empty list")
        seeds = []
    if isinstance(items, int) and not isinstance(items, bool) and isinstance(seeds, list):
        expected = items * len(seeds)
        if len(rows) != expected:
            add(f"row count {len(rows)} != manifest items × seeds ({expected})")

    def pair_set(source_rows: list[dict], label: str) -> set[tuple[str, int]]:
        pairs: list[tuple[str, int]] = []
        for index, row in enumerate(source_rows):
            if not isinstance(row, dict):
                add(f"{label} row {index} is not an object")
                continue
            item_id, seed = row.get("item_id"), row.get("seed")
            if not isinstance(item_id, str) or not item_id or not isinstance(seed, int) or isinstance(seed, bool):
                add(f"{label} row {index} has invalid item_id/seed")
                continue
            pairs.append((item_id, seed))
        if len(pairs) != len(set(pairs)):
            add(f"{label} contains duplicate (item_id, seed) rows")
        return set(pairs)

    pr_pairs = pair_set(rows, "PR")
    base_pairs = pair_set(base_rows, "baseline")
    if pr_pairs != base_pairs:
        add("(item_id, seed) pairs differ from baseline")

    failures = pr.get("evaluator_failures")
    if failures:
        add(f"evaluator_failures is non-empty ({len(failures) if hasattr(failures, '__len__') else 'unknown'})")

    metric_specs = spec.get("metrics") or []
    # Per-row graders must produce a value for every row. Aggregate-only metrics
    # (for example pass_hat_5 and cost_per_success) are computed after evaluation.
    for entry in metric_specs:
        if not isinstance(entry, dict):
            continue
        metric_id = entry.get("id")
        grader = entry.get("grader")
        row_graded = grader in ("code", "lab8.metrics.trial_pass") or any(
            isinstance(row, dict) and metric_id in row for row in rows
        )
        if row_graded and metric_id:
            for index, row in enumerate(rows):
                if not isinstance(row, dict) or row.get(metric_id) is None:
                    add(f"graded metric {metric_id} is missing/None in PR row {index}")

    # Slice membership is part of the evaluated dataset, not mutable PR metadata.
    def item_slices(source_rows: list[dict], label: str) -> dict[str, set[str]]:
        result: dict[str, set[str]] = {}
        for row in source_rows:
            if not isinstance(row, dict) or not isinstance(row.get("item_id"), str):
                continue
            tags = row.get("slices") or []
            if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
                add(f"{label} has invalid slice tags for {row['item_id']}")
                continue
            tag_set = set(tags)
            item_id = row["item_id"]
            if item_id in result and result[item_id] != tag_set:
                add(f"{label} has inconsistent slice tags for {item_id}")
            result[item_id] = tag_set
        return result

    pr_slices = item_slices(rows, "PR")
    base_slices = item_slices(base_rows, "baseline")
    for item_id in pr_slices.keys() & base_slices.keys():
        if pr_slices[item_id] != base_slices[item_id]:
            add(f"slice tags changed for item {item_id}")

    # Ratchet only applies when both specs describe the same eval-set version.
    if base_spec is not None and spec.get("eval_set_version") == base_spec.get("eval_set_version"):
        current_metrics = {m.get("id"): m for m in spec.get("metrics") or [] if isinstance(m, dict) and m.get("id")}
        previous_metrics = {m.get("id"): m for m in base_spec.get("metrics") or [] if isinstance(m, dict) and m.get("id")}
        for metric_id, previous in previous_metrics.items():
            current = current_metrics.get(metric_id)
            if current is None:
                add(f"ratchet: metric {metric_id} was removed")
                continue
            old_th, new_th = previous.get("threshold") or {}, current.get("threshold") or {}
            for bound, loosened in (("max", lambda new, old: new > old),
                                    ("min", lambda new, old: new < old)):
                if bound in old_th and (bound not in new_th or loosened(new_th[bound], old_th[bound])):
                    add(f"ratchet: {metric_id} {bound} threshold was loosened or removed")
            if previous.get("blocking") and not current.get("blocking"):
                add(f"ratchet: {metric_id} changed from blocking to non-blocking")
            if old_th.get("no_significant_drop") and not new_th.get("no_significant_drop"):
                add(f"ratchet: {metric_id} removed no_significant_drop")

        def slice_key(entry: dict) -> tuple[str, str]:
            return entry.get("name", ""), entry.get("metric", "")

        current_slices = {slice_key(s): s for s in spec.get("slices") or [] if isinstance(s, dict)}
        previous_slices = {slice_key(s): s for s in base_spec.get("slices") or [] if isinstance(s, dict)}
        for key, previous in previous_slices.items():
            current = current_slices.get(key)
            label = f"{key[0]}/{key[1]}"
            if current is None:
                add(f"ratchet: slice {label} was removed")
                continue
            for bound, loosened in (("max", lambda new, old: new > old),
                                    ("min", lambda new, old: new < old)):
                if bound in previous and (bound not in current or loosened(current[bound], previous[bound])):
                    add(f"ratchet: slice {label} {bound} threshold was loosened or removed")
            if previous.get("blocking") and not current.get("blocking"):
                add(f"ratchet: slice {label} changed from blocking to non-blocking")
            if previous.get("no_significant_drop") and not current.get("no_significant_drop"):
                add(f"ratchet: slice {label} removed no_significant_drop")

    return problems

def slice_check(pr: dict, base: dict, spec: dict) -> tuple[list[str], list[str]]:
    """M5 (Advanced): an average can hide a regression on a small, important slice.
    For each entry of spec["slices"] ({"name", "metric", "min"?, "no_significant_drop"?, "blocking"}):
      - value = mean of per_item(pr, metric, slice_name=name)
      - fail if below "min", or if no_significant_drop and the paired CI over the slice's items
        lies entirely below 0
    Return (blocked ids like "slice:money_movement/pass_rate", report lines)."""
    blocked: list[str] = []
    lines: list[str] = []
    bs = spec.get("bootstrap", {})

    for entry in spec.get("slices") or []:
        name = entry["name"]
        metric = entry["metric"]
        slice_id = f"slice:{name}/{metric}"
        current = per_item(pr, metric, slice_name=name)
        previous = per_item(base, metric, slice_name=name)
        verdict = "ok"
        notes: list[str] = []

        if not current:
            verdict = "missing"
            notes.append("no PR rows in slice")
        else:
            value = sum(current.values()) / len(current)
            if "min" in entry and value < entry["min"]:
                verdict = "fail"
                notes.append(f"mean {value:.3f} < min {entry['min']:.3f}")

            if entry.get("no_significant_drop"):
                keys = sorted(set(current) & set(previous))
                if not keys:
                    verdict = "missing"
                    notes.append("no paired baseline items in slice")
                else:
                    delta, low, high = stats.paired_bootstrap(
                        [current[k] for k in keys],
                        [previous[k] for k in keys],
                        n_resamples=bs.get("n_resamples", 1000),
                        rng=bs.get("rng", 2027),
                        confidence=bs.get("confidence", 0.95),
                    )
                    notes.append(f"Δ {delta:+.3f} CI [{low:+.3f}, {high:+.3f}]")
                    if high < 0:
                        verdict = "fail"

        if verdict != "ok" and entry.get("blocking"):
            blocked.append(slice_id)
        label = "ok" if verdict == "ok" else ("MISSING" if verdict == "missing" else
                                                ("BLOCK" if entry.get("blocking") else "warn"))
        lines.append(f"  {slice_id:<38} {json.dumps(entry):<55} {'; '.join(notes):<36} {label}")
    return blocked, lines


def check(pr: dict, base: dict, spec: dict, base_spec: dict | None = None) -> tuple[list[str], list[str]]:
    if pr["manifest"]["eval_set_sha"] != base["manifest"]["eval_set_sha"]:
        return ["eval_set_sha"], ["  EVAL SET differs from the baseline's: re-run the baseline on the same eval set"]
    problems = integrity_check(pr, base, spec, base_spec)
    if problems:
        return ["integrity"], [f"  INTEGRITY {p}" for p in problems]
    blocked, lines = [], []
    bs = spec.get("bootstrap", {})
    for m in spec["metrics"]:
        mid, th, val = m["id"], m.get("threshold", {}), pr["metrics"].get(m["id"])
        verdict, note = "ok", ""
        if val is None:
            verdict = "missing"
        elif "max" in th and val > th["max"]:
            verdict = "fail"
        elif "min" in th and val < th["min"]:
            verdict = "fail"
        elif "max_increase" in th and base["metrics"].get(mid):
            if val > base["metrics"][mid] * (1 + th["max_increase"]):
                verdict = "fail"
        if th.get("no_significant_drop") and val is not None:
            a, b = per_item(pr, mid), per_item(base, mid)
            keys = sorted(set(a) & set(b))
            d, lo, hi = stats.paired_bootstrap([a[k] for k in keys], [b[k] for k in keys],
                                               n_resamples=bs.get("n_resamples", 1000), rng=bs.get("rng", 2027))
            note = f"Δ {d:+.3f} CI [{lo:+.3f}, {hi:+.3f}]"
            if hi < 0:
                verdict = "fail"
        if verdict != "ok" and m.get("blocking"):
            blocked.append(mid)
        label = {"ok": "ok", "missing": "MISSING"}.get(verdict, "BLOCK" if m.get("blocking") else "warn")
        lines.append(f"  {mid:<22} {val!s:<8} {json.dumps(th):<40} {note:<28} {label}")
    if spec.get("slices"):
        sb, sl = slice_check(pr, base, spec)
        blocked += sb
        lines += sl
    return blocked, lines


def main(argv: list[str] | None = None) -> int:
    utf8_stdio()
    ap = argparse.ArgumentParser(prog="lab9.gate")
    ap.add_argument("--pr", required=True)
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--spec", default=str(SPEC))
    ap.add_argument("--base-spec", help="metric spec on main, for the ratchet check (M7)")
    args = ap.parse_args(argv)
    pr = json.loads(Path(args.pr).read_text(encoding="utf-8"))
    base = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    base_spec = load_spec(Path(args.base_spec)) if args.base_spec else None
    blocked, lines = check(pr, base, load_spec(Path(args.spec)), base_spec)
    print(f"gate: PR {pr['run_id']} vs main {base['run_id']} · eval set {pr['manifest']['eval_set_sha']}")
    print("\n".join(lines))
    if blocked:
        print(f"exit 1 — blocked: {', '.join(blocked)}")
        return 1
    print("exit 0 — merge")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
