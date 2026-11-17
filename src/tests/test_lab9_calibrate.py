import pytest

from lab9.calibrate import compare_reports


def make_report(seeds, pass_values):
    rows = []
    for item_index, (item_id, values) in enumerate(pass_values.items()):
        for seed, passed in zip(seeds, values, strict=True):
            rows.append({
                "item_id": item_id,
                "seed": seed,
                "pass_rate": passed,
                "refund_amount_correct": passed,
                "slices": ["money_movement"],
            })
    return {
        "shape": "swarm",
        "manifest": {
            "eval_set_sha": "abc123",
            "items": len(pass_values),
            "seeds": seeds,
        },
        "rows": rows,
        "evaluator_failures": [],
        "metrics": {
            "pass_rate": 0.8,
            "refund_amount_correct": 0.8,
            "pass_hat_5": 0.5,
            "cost_per_success": 10.0,
        },
    }


def test_compare_reports_calculates_paired_aa_noise():
    seeds_a = [11, 22, 33, 44, 55]
    seeds_b = [66, 77, 88, 99, 110]
    report_a = make_report(seeds_a, {
        "I-1": [True, True, True, True, True],
        "I-2": [True, True, True, True, False],
    })
    report_b = make_report(seeds_b, {
        "I-1": [True, True, True, True, False],
        "I-2": [True, True, True, True, False],
    })

    result = compare_reports(report_a, report_b, n_resamples=100, rng=7)

    assert result["calibration"] == "A/A"
    assert result["metrics"]["pass_rate"]["items"] == 2
    assert result["metrics"]["pass_hat_5"]["mean_a"] == 0.5
    assert result["metrics"]["pass_hat_5"]["mean_b"] == 0.0
    assert result["metrics"]["pass_hat_5"]["delta_a_minus_b"] == 0.5
    assert result["metrics"]["pass_hat_5"]["noise_margin_95"] >= 0.0


def test_compare_reports_rejects_overlapping_seed_sets():
    report_a = make_report([11, 22, 33, 44, 55], {"I-1": [True] * 5})
    report_b = make_report([11, 66, 77, 88, 99], {"I-1": [True] * 5})

    with pytest.raises(ValueError, match="disjoint"):
        compare_reports(report_a, report_b)


def test_compare_reports_rejects_different_eval_sets():
    report_a = make_report([11, 22, 33, 44, 55], {"I-1": [True] * 5})
    report_b = make_report([66, 77, 88, 99, 110], {"I-1": [True] * 5})
    report_b["manifest"]["eval_set_sha"] = "different"

    with pytest.raises(ValueError, match="different eval_set_sha"):
        compare_reports(report_a, report_b)
