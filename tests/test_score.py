from src.performance.score import compute_score, grade


def test_idle_machine_scores_high(make_snapshot):
    score, _ = compute_score(make_snapshot())
    assert score >= 90 and grade(score) == "Excellent"


def test_stressed_machine_scores_low(make_snapshot):
    score, _ = compute_score(make_snapshot(cpu=99, ram=97, temp=92, disk=95))
    assert score < 30


def test_score_drops_as_cpu_rises(make_snapshot):
    assert compute_score(make_snapshot(cpu=95))[0] < compute_score(make_snapshot(cpu=20))[0]


def test_gpu_is_optional(make_snapshot):
    assert "gpu" not in compute_score(make_snapshot())[1]
    assert "gpu" in compute_score(make_snapshot(gpu=40))[1]
