"""Compare two independent seed batches for an A/A calibration run.

Run from src:
  python -m lab9.calibrate --a reports/aa_a.json --b reports/aa_b.json
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from lab9 import stats


def _validate_report(report: dict[str, Any], label: str) -> tuple[dict[str, Any], dict[str, dict[int, dict[str, Any]]]]:
    if not isinstance(report, dict) or not isinstance(report.get("manifest"), dict):
        raise ValueError(f"{label}: missing manifest")
    manifest = report["manifest"]
    if not manifest.get("eval_set_sha"):
        raise ValueError(f"{label}: missing manifest.eval_set_sha")
    if not isinstance(report.get("rows"), list) or not report["rows"]:
        raise ValueError(f"{label}: rows must be a non-empty list")
    if report.get("evaluator_failures"):
        raise ValueError(f"{label}: evaluator_failures is non-empty")
    grouped: dict[str, dict[int, dict[str, Any]]] = defaultdict(dict)
    for index, row in enumerate(report["rows"]):
        if not isinstance(row, dict):
            raise ValueError(f"{label}: row {index} is not an object")
        item_id, seed = row.get("item_id"), row.get("seed")
        if not isinstance(item_id, str) or not item_id or isinstance(seed, bool) or not isinstance(seed, int):
            raise ValueError(f"{label}: row {index} has invalid item_id/seed")
        if seed in grouped[item_id]:
            raise ValueError(f"{label}: duplicate row for {item_id}@{seed}")
        grouped[item_id][seed] = row
    seeds = manifest.get("seeds")
    if not isinstance(seeds, list) or not seeds or len(seeds) != len(set(seeds)):
        raise ValueError(f"{label}: manifest.seeds must be a non-empty unique list")
    expected = set(seeds)
    for item_id, item_rows in grouped.items():
        if set(item_rows) != expected:
            raise ValueError(f"{label}: {item_id} seeds do not match manifest.seeds")
    if len(grouped) != manifest.get("items"):
        raise ValueError(f"{label}: manifest.items does not match distinct item count")
    return manifest, grouped


def _per_item(grouped: dict[str, dict[int, dict[str, Any]]], metric: str) -> dict[str, float]:
    values: dict[str, float] = {}
    for item_id, seed_rows in grouped.items():
        raw = [row.get(metric) for row in seed_rows.values()]
        if any(value is None or isinstance(value, bool) and metric != "pass_rate"
               or not isinstance(value, (int, float, bool)) for value in raw):
            continue
        values[item_id] = sum(float(value) for value in raw) / len(raw)
    return values


def compare_reports(report_a: dict[str, Any], report_b: dict[str, Any], *,
                    n_resamples: int = 5000, rng: int = 2027) -> dict[str, Any]:
    manifest_a, grouped_a = _validate_report(report_a, "A")
    manifest_b, grouped_b = _validate_report(report_b, "B")
    if manifest_a["eval_set_sha"] != manifest_b["eval_set_sha"]:
        raise ValueError("A/A reports use different eval_set_sha")
    if report_a.get("shape") != report_b.get("shape"):
        raise ValueError("A/A reports use different shapes")
    if set(manifest_a["seeds"]) & set(manifest_b["seeds"]):
        raise ValueError("A/A seed sets must be disjoint")
    if set(grouped_a) != set(grouped_b):
        raise ValueError("A/A item_id sets differ")

    metrics_a = report_a.get("metrics") or {}
    metrics_b = report_b.get("metrics") or {}
    metric_ids = sorted((set(metrics_a) & set(metrics_b)) - {"pass_5"})
    results: dict[str, Any] = {}
    for metric in metric_ids:
        a_values, b_values = _per_item(grouped_a, metric), _per_item(grouped_b, metric)
        keys = sorted(set(a_values) & set(b_values))
        if not keys:
            continue
        delta, low, high = stats.paired_bootstrap(
            [a_values[key] for key in keys], [b_values[key] for key in keys],
            n_resamples=n_resamples, rng=rng,
        )
        results[metric] = {
            "items": len(keys),
            "mean_a": round(sum(a_values[k] for k in keys) / len(keys), 6),
            "mean_b": round(sum(b_values[k] for k in keys) / len(keys), 6),
            "delta_a_minus_b": round(delta, 6),
            "ci95": [round(low, 6), round(high, 6)],
            "noise_margin_95": round(max(abs(low), abs(high)), 6),
            "ci_contains_zero": low <= 0 <= high,
        }

    # pass_hat_5 is derived separately per item from that batch's five pass_rate trials.
    if len(manifest_a["seeds"]) == 5 and len(manifest_b["seeds"]) == 5:
        per_batch: list[dict[str, float]] = []
        for grouped in (grouped_a, grouped_b):
            per_batch.append({
                item_id: stats.pass_hat_k(
                    len(rows), sum(bool(row.get("pass_rate")) for row in rows.values()), 5
                )
                for item_id, rows in grouped.items()
            })
        keys = sorted(set(per_batch[0]) & set(per_batch[1]))
        delta, low, high = stats.paired_bootstrap(
            [per_batch[0][key] for key in keys], [per_batch[1][key] for key in keys],
            n_resamples=n_resamples, rng=rng,
        )
        results["pass_hat_5"] = {
            "items": len(keys),
            "mean_a": round(sum(per_batch[0][k] for k in keys) / len(keys), 6),
            "mean_b": round(sum(per_batch[1][k] for k in keys) / len(keys), 6),
            "delta_a_minus_b": round(delta, 6),
            "ci95": [round(low, 6), round(high, 6)],
            "noise_margin_95": round(max(abs(low), abs(high)), 6),
            "ci_contains_zero": low <= 0 <= high,
        }
    else:
        results["pass_hat_5"] = {"status": "not_calculated", "reason": "each batch must contain exactly five seeds"}

    return {
        "calibration": "A/A",
        "shape": report_a.get("shape"),
        "eval_set_sha": manifest_a["eval_set_sha"],
        "items": len(grouped_a),
        "seeds_a": manifest_a["seeds"],
        "seeds_b": manifest_b["seeds"],
        "metrics": results,
        "interpretation": (
            "noise_margin_95 is the largest absolute endpoint of the paired 95% CI for A-B. "
            "Use it as an empirical noise reference for this dataset/agent/seed design; "
            "A/A alone cannot establish an absolute quality floor. Keep pass_hat_5 min provisional "
            "until a separate minimum acceptable quality target is chosen."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="lab9.calibrate")
    parser.add_argument("--a", required=True, help="first A/A report JSON")
    parser.add_argument("--b", required=True, help="second A/A report JSON")
    parser.add_argument("--out", default="reports/aa_calibration.json")
    parser.add_argument("--resamples", type=int, default=5000)
    parser.add_argument("--rng", type=int, default=2027)
    args = parser.parse_args(argv)
    report_a = json.loads(Path(args.a).read_text(encoding="utf-8"))
    report_b = json.loads(Path(args.b).read_text(encoding="utf-8"))
    result = compare_reports(report_a, report_b, n_resamples=args.resamples, rng=args.rng)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"A/A calibration · {result['shape']} · {result['items']} items · eval {result['eval_set_sha']}")
    for metric, values in result["metrics"].items():
        if "ci95" not in values:
            print(f"  {metric:<24} {values['status']}: {values['reason']}")
            continue
        print(f"  {metric:<24} A={values['mean_a']:.4f} B={values['mean_b']:.4f} "
              f"Δ={values['delta_a_minus_b']:+.4f} CI95=[{values['ci95'][0]:+.4f}, {values['ci95'][1]:+.4f}] "
              f"noise≤{values['noise_margin_95']:.4f}")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
