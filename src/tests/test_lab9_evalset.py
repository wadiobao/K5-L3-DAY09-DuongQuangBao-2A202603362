"""M0 command-line checks run before completing the M1 taxonomy."""

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


@pytest.fixture
def evalset_cli(tmp_path):
    source = tmp_path / "data/public_claims.jsonl"
    source.parent.mkdir()
    claim = {"claim_id": "C-001", "matrix_id": "T01", "expected": {"refund_vnd": 35000}}
    source.write_text(json.dumps(claim) + "\n", encoding="utf-8")

    def run_evalset(*args):
        return subprocess.run(
            [sys.executable, "-m", "lab9.evalset", *args],
            cwd=tmp_path,
            env={**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])},
            capture_output=True,
            text=True,
        )

    return run_evalset


def test_build_writes_items_and_labels_without_checking_tags(tmp_path, evalset_cli):
    result = evalset_cli("--build")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "problem(s)" not in result.stdout
    item = json.loads((tmp_path / "data/eval/eval_set_v1.jsonl").read_text(encoding="utf-8"))
    labels = json.loads((tmp_path / "data/eval/labels_v1.json").read_text(encoding="utf-8"))
    assert item["claim_id"] == "C-001"
    assert "expected" not in item
    assert labels == {"C-001": {"refund_vnd": 35000}}


def test_explicit_check_runs_after_build(tmp_path, evalset_cli):
    result = evalset_cli("--build", "--check")
    item = json.loads((tmp_path / "data/eval/eval_set_v1.jsonl").read_text(encoding="utf-8"))
    expected_problems = int(not item["failure_modes"])
    assert result.returncode == expected_problems, result.stdout + result.stderr
    assert f"{expected_problems} problem(s)" in result.stdout


def test_check_rejects_missing_tags(tmp_path, evalset_cli):
    evalset_cli("--build")
    items_path = tmp_path / "data/eval/eval_set_v1.jsonl"
    item = json.loads(items_path.read_text(encoding="utf-8"))
    item["failure_modes"] = []
    items_path.write_text(json.dumps(item) + "\n", encoding="utf-8")

    result = evalset_cli("--check")
    assert result.returncode == 1, result.stdout + result.stderr
    assert "failure_modes empty" in result.stdout

def test_build_records_trace_provenance_for_each_failure_mode(tmp_path, evalset_cli):
    result = evalset_cli("--build")
    assert result.returncode == 0, result.stdout + result.stderr
    item = json.loads((tmp_path / "data/eval/eval_set_v1.jsonl").read_text(encoding="utf-8"))
    provenance = item["provenance"]
    assert provenance["generator"] == "lab9.trace_case"
    assert provenance["checked_by"] is None
    assert set(provenance["from_trace"]) == set(item["failure_modes"])
    assert all(command.startswith("python -m lab9.trace_case ") for command in provenance["from_trace"].values())


def test_check_rejects_missing_trace_provenance(tmp_path, evalset_cli):
    evalset_cli("--build")
    items_path = tmp_path / "data/eval/eval_set_v1.jsonl"
    item = json.loads(items_path.read_text(encoding="utf-8"))
    item["provenance"]["from_trace"].pop("FM-01")
    items_path.write_text(json.dumps(item) + "\n", encoding="utf-8")

    result = evalset_cli("--check")
    assert result.returncode == 1, result.stdout + result.stderr
    assert "missing provenance.from_trace for FM-01" in result.stdout


def test_check_rejects_malformed_trace_command(tmp_path, evalset_cli):
    evalset_cli("--build")
    items_path = tmp_path / "data/eval/eval_set_v1.jsonl"
    item = json.loads(items_path.read_text(encoding="utf-8"))
    item["provenance"]["from_trace"]["FM-01"] = "python something else"
    items_path.write_text(json.dumps(item) + "\n", encoding="utf-8")

    result = evalset_cli("--check")
    assert result.returncode == 1, result.stdout + result.stderr
    assert "invalid trace command for FM-01" in result.stdout

