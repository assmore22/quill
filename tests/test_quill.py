"""Tests for QUILL (direct runner). AI judge_entry() validated live on studionet."""
from pathlib import Path

CONTRACT = str(Path(__file__).resolve().parents[1] / "contracts" / "quill.py")
GEN = 10 ** 18
C_OPEN = 0; C_CLOSED = 1; E_PENDING = 0


def _open(q, vm, who, title="Essay Prize", prompt="Why consensus matters", rubric="Clarity and insight", prize=10):
    vm.sender = who; vm.value = prize * GEN
    cid = q.open_contest(title, prompt, rubric); vm.value = 0
    return cid


def test_open_contest(deploy, direct_vm, direct_alice):
    q = deploy(CONTRACT)
    cid = _open(q, direct_vm, direct_alice)
    assert cid == 0
    c = q.get_contest(0)
    assert c["status"] == C_OPEN
    assert int(c["prize"]) == 10 * GEN
    assert c["has_winner"] == 0


def test_open_requires_prize(deploy, direct_vm, direct_alice):
    q = deploy(CONTRACT)
    direct_vm.sender = direct_alice; direct_vm.value = 0
    with direct_vm.expect_revert("fund a prize pool"):
        q.open_contest("t", "p", "r")


def test_open_requires_prompt(deploy, direct_vm, direct_alice):
    q = deploy(CONTRACT)
    direct_vm.sender = direct_alice; direct_vm.value = GEN
    with direct_vm.expect_revert("a prompt is required"):
        q.open_contest("t", "", "r")
    direct_vm.value = 0


def test_submit_entry(deploy, direct_vm, direct_alice, direct_bob):
    q = deploy(CONTRACT)
    _open(q, direct_vm, direct_alice)
    direct_vm.sender = direct_bob
    eid = q.submit_entry(0, "My Entry", "https://example.com/essay")
    assert eid == 0
    e = q.get_entry(0)
    assert e["status"] == E_PENDING
    assert e["contest_id"] == 0
    assert e["title"] == "My Entry"


def test_submit_requires_url(deploy, direct_vm, direct_alice, direct_bob):
    q = deploy(CONTRACT)
    _open(q, direct_vm, direct_alice)
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("a public URL is required"):
        q.submit_entry(0, "t", "")


def test_award_requires_judged(deploy, direct_vm, direct_alice):
    q = deploy(CONTRACT)
    _open(q, direct_vm, direct_alice)
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("no judged entry"):
        q.award(0)


def test_judge_bad_id(deploy, direct_vm, direct_alice):
    q = deploy(CONTRACT)
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("no such entry"):
        q.judge_entry(0)


def test_multiple(deploy, direct_vm, direct_alice, direct_bob):
    q = deploy(CONTRACT)
    _open(q, direct_vm, direct_alice, title="Prize A")
    _open(q, direct_vm, direct_alice, title="Prize B")
    direct_vm.sender = direct_bob
    q.submit_entry(0, "E1", "https://a.com")
    q.submit_entry(1, "E2", "https://b.com")
    assert q.get_contest_count() == 2
    assert q.get_entry_count() == 2
    assert q.get_entry(1)["contest_id"] == 1
