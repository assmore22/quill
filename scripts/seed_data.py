"""Seed QUILL with real on-chain data on studionet."""
from pathlib import Path

from gltest_cli.config.general import get_general_config
from gltest_cli.config.user import load_user_config
from gltest import get_contract_factory, get_default_account

ROOT = Path(__file__).resolve().parents[1]
ADDR = "0x3682b72Fe449aceF1330c15fefa5E1e05e413F6f"
GEN = 10 ** 18

cfg = load_user_config(str(ROOT / "gltest.config.yaml"))
get_general_config().user_config = cfg
c = get_contract_factory(contract_file_path=str(ROOT / "contracts" / "quill.py")).build_contract(
    ADDR, account=get_default_account())

ENTRIES = [
    ("Notes on a Reserved Domain", "https://example.com"),
    ("The Example, Examined", "https://example.com"),
]


def main():
    if c.get_contest_count().call() == 0:
        c.open_contest(args=[
            "The Consensus Essay Prize",
            "Argue why agreement between independent parties is the root of trust online.",
            "Score on clarity, originality, and whether it makes a concrete, well-supported argument.",
        ]).transact(value=10 * GEN)
        print("contest opened")
    if c.get_entry_count().call() == 0:
        for (t, u) in ENTRIES:
            c.submit_entry(args=[0, t, u]).transact()
            print("submitted:", t)
    for eid in range(c.get_entry_count().call()):
        e = c.get_entry(args=[eid]).call()
        if int(e["status"]) == 0:
            print("judging", eid, "(AI)...")
            try:
                c.judge_entry(args=[eid]).transact()
            except Exception as ex:
                print("judge", eid, "->", ex)
    for eid in range(c.get_entry_count().call()):
        e = c.get_entry(args=[eid]).call()
        print("entry", eid, "score=", e["score"], "|", e["title"], "|", (e["rationale"] or "")[:50])
    cc = c.get_contest(args=[0]).call()
    if int(cc["status"]) == 0 and int(cc["has_winner"]) == 1:
        print("awarding... best_score=", cc["best_score"])
        try:
            c.award(args=[0]).transact(); print("awarded")
        except Exception as ex:
            print("award ->", ex)
    cc = c.get_contest(args=[0]).call()
    print("contest status=", ["OPEN", "CLOSED"][int(cc["status"])], "winner_score=", cc["best_score"])


if __name__ == "__main__":
    main()
