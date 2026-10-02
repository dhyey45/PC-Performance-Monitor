from src.alerts import AlertManager


def test_no_alerts_when_idle(make_snapshot):
    assert AlertManager().check(make_snapshot()) == []


def test_cpu_alert_and_cooldown(make_snapshot):
    mgr = AlertManager()
    first = mgr.check(make_snapshot(cpu=95))
    assert [a.metric for a in first] == ["CPU"] and first[0].level == "critical"
    assert mgr.check(make_snapshot(cpu=95)) == []  # still cooling down


def test_critical_level(make_snapshot):
    assert AlertManager().check(make_snapshot(ram=99))[0].level == "critical"
