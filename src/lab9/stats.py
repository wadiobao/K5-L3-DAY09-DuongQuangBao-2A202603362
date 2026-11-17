"""Statistics students implement (M2 judge calibration, M4 paired bootstrap).

Rules: a judge is a classifier -- measure it like one. A higher mean is not
"better" until the paired CI of the difference excludes 0.
Reference values to self-check are in tests/test_lab9_stats.py.
"""

from __future__ import annotations

from collections.abc import Sequence
from math import comb

POS = "FAIL"   # the judge's job is to FIND failures, so FAIL is the positive class


def confusion(human: Sequence[str], judge: Sequence[str]) -> dict[str, int]:
    """tp/fp/fn/tn with FAIL as positive."""
    tp = fp = fn = tn = 0
    for h, j in zip(human, judge, strict=True):
        if j == POS:
            if h == POS:
                tp += 1
            else:
                fp += 1
        elif h == POS:
            fn += 1
        else:
            tn += 1
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn}


def precision_recall(human: Sequence[str], judge: Sequence[str]) -> tuple[float, float]:
    c = confusion(human, judge)
    precision = c["tp"] / (c["tp"] + c["fp"]) if c["tp"] + c["fp"] else 0.0
    recall = c["tp"] / (c["tp"] + c["fn"]) if c["tp"] + c["fn"] else 0.0
    return precision, recall


def cohen_kappa(human: Sequence[str], judge: Sequence[str]) -> float:
    """(docstring giữ nguyên)"""
    n = len(human)
    if n == 0:
        raise ValueError("kappa undefined: no items")
    c = confusion(human, judge)
    p_o = (c["tp"] + c["tn"]) / n
    human_fail = (c["tp"] + c["fn"]) / n
    judge_fail = (c["tp"] + c["fp"]) / n
    p_e = human_fail * judge_fail + (1 - human_fail) * (1 - judge_fail)
    if p_e == 1:
        raise ValueError("kappa undefined: chance agreement is 1 (constant labels)")
    return (p_o - p_e) / (1 - p_e)


def rogan_gladen(observed_rate: float, sensitivity: float, specificity: float) -> float:
    """(docstring giữ nguyên)"""
    denom = sensitivity + specificity - 1
    if denom <= 0:
        raise ValueError("Rogan-Gladen undefined: sensitivity + specificity must exceed 1")
    return min(1.0, max(0.0, (observed_rate + specificity - 1) / denom))


def paired_bootstrap(a: Sequence[float], b: Sequence[float], *, n_resamples: int = 1000,
                     rng: int = 2027, confidence: float = 0.95) -> tuple[float, float, float]:
    """Return mean(a-b) and a paired percentile-bootstrap confidence interval.

    Uses the exact empirical bootstrap distribution when it has at most 200,000
    resamples; otherwise uses deterministic Monte Carlo resampling. This keeps
    the evaluator independent of NumPy/SciPy.
    """
    import itertools
    import random

    if len(a) != len(b) or not a:
        raise ValueError("a and b must be non-empty sequences of the same length (same items, same order)")
    if isinstance(n_resamples, bool) or not isinstance(n_resamples, int) or n_resamples < 1:
        raise ValueError("n_resamples must be a positive integer")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")

    differences = [float(x) - float(y) for x, y in zip(a, b, strict=True)]
    observed = sum(differences) / len(differences)
    if all(value == differences[0] for value in differences):
        return observed, observed, observed

    n = len(differences)
    exact_count = n ** n
    if exact_count <= 200_000:
        samples = (
            sum(differences[index] for index in indices) / n
            for indices in itertools.product(range(n), repeat=n)
        )
        estimates = sorted(samples)
    else:
        randomizer = random.Random(rng)
        estimates = sorted(
            sum(differences[randomizer.randrange(n)] for _ in range(n)) / n
            for _ in range(n_resamples)
        )

    alpha = (1.0 - confidence) / 2.0

    def percentile(values: list[float], probability: float) -> float:
        position = (len(values) - 1) * probability
        lower = int(position)
        upper = min(lower + 1, len(values) - 1)
        fraction = position - lower
        return values[lower] + (values[upper] - values[lower]) * fraction

    return observed, percentile(estimates, alpha), percentile(estimates, 1.0 - alpha)


def _validate_pass_k_args(n: int, c: int, k: int) -> None:
    """Validate counts shared by pass@k and pass^k."""
    if any(isinstance(x, bool) or not isinstance(x, int) for x in (n, c, k)):
        raise ValueError("n, c, and k must be integers")
    if n < 1:
        raise ValueError("n must be at least 1")
    if not 0 <= c <= n:
        raise ValueError("c must be between 0 and n")
    if not 1 <= k <= n:
        raise ValueError("k must be between 1 and n")


def pass_at_k(n: int, c: int, k: int) -> float:
    """Unbiased pass@k estimator: 1 - C(n-c, k) / C(n, k).

    n is the number of sampled trials, c the number that passed, and k the
    number of attempts allowed. Returns 1 when fewer than k failures exist.
    """
    _validate_pass_k_args(n, c, k)
    return 1.0 - comb(n - c, k) / comb(n, k)


def pass_hat_k(n: int, c: int, k: int) -> float:
    """Unbiased pass^k estimator: C(c, k) / C(n, k), the probability that
    all k trials drawn without replacement pass. pass^k <= pass@1 <= pass@k.
    """
    _validate_pass_k_args(n, c, k)
    return comb(c, k) / comb(n, k) if c >= k else 0.0
