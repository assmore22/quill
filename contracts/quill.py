# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""
QUILL - AI-Judged Writing Contest
=================================
A host opens a contest with a prompt, a judging rubric, and a prize pool. Writers
submit an entry as a public URL. To judge an entry, the contract reads it against
the prompt and rubric and a validator set agrees (Equivalence Principle) on a
score from 0 to 100. The highest-scored entry wins the whole pool. Judging is
transparent: every score and its reasoning is recorded on-chain.

Contest status:  OPEN(0) -> CLOSED(1, prize awarded)
Entry status:    PENDING(0) -> JUDGED(1)
"""

from genlayer import *
from dataclasses import dataclass
import json
import typing


C_OPEN = 0
C_CLOSED = 1
E_PENDING = 0
E_JUDGED = 1


@allow_storage
@dataclass
class Contest:
    host: Address
    title: str
    prompt: str
    rubric: str
    prize: u256
    status: u8
    winner: Address
    best_score: u256
    has_winner: u8


@allow_storage
@dataclass
class Entry:
    contest_id: u256
    author: Address
    title: str
    url: str
    score: u256
    status: u8
    rationale: str


class Quill(gl.Contract):
    contests: DynArray[Contest]
    entries: DynArray[Entry]

    def __init__(self) -> None:
        pass

    @gl.public.write.payable
    def open_contest(self, title: str, prompt: str, rubric: str) -> int:
        if len(title.strip()) == 0:
            raise gl.vm.UserError("a title is required")
        if len(prompt.strip()) == 0:
            raise gl.vm.UserError("a prompt is required")
        if len(rubric.strip()) == 0:
            raise gl.vm.UserError("a judging rubric is required")
        prize = gl.message.value
        if prize == u256(0):
            raise gl.vm.UserError("fund a prize pool to open a contest")
        c = self.contests.append_new_get()
        c.host = gl.message.sender_address
        c.title = title
        c.prompt = prompt
        c.rubric = rubric
        c.prize = prize
        c.status = u8(C_OPEN)
        c.winner = Address(bytes(20))
        c.best_score = u256(0)
        c.has_winner = u8(0)
        return len(self.contests) - 1

    @gl.public.write
    def submit_entry(self, contest_id: int, title: str, url: str) -> int:
        c = self._get_contest(contest_id)
        if c.status != C_OPEN:
            raise gl.vm.UserError("contest is closed")
        if len(title.strip()) == 0:
            raise gl.vm.UserError("an entry title is required")
        if len(url.strip()) == 0:
            raise gl.vm.UserError("a public URL is required")
        e = self.entries.append_new_get()
        e.contest_id = u256(contest_id)
        e.author = gl.message.sender_address
        e.title = title
        e.url = url
        e.score = u256(0)
        e.status = u8(E_PENDING)
        e.rationale = ""
        return len(self.entries) - 1

    @gl.public.write
    def judge_entry(self, entry_id: int) -> None:
        """Read the entry against the prompt and rubric; validators agree on a
        score from 0 to 100. The best score so far becomes the provisional winner."""
        e = self._get_entry(entry_id)
        if e.status != E_PENDING:
            raise gl.vm.UserError("entry already judged")
        c = self.contests[int(e.contest_id)]
        if c.status != C_OPEN:
            raise gl.vm.UserError("contest is closed")

        prompt = c.prompt
        rubric = c.rubric
        url = e.url

        def leader_fn() -> str:
            page = ""
            try:
                page = gl.nondet.web.get(url).body.decode("utf-8")[:6000]
            except Exception:
                page = "(entry page unreachable)"
            prompt_text = (
                f"Writing contest prompt:\n{prompt}\n\n"
                f"Judging rubric:\n{rubric}\n\n"
                f"Submitted entry:\n{page}\n\n"
                "As an impartial judge, score this entry from 0 to 100 against the "
                "prompt and rubric. Reply with ONLY JSON: {\"score\": <0-100>, "
                "\"reason\": \"<short justification>\"}."
            )
            return gl.nondet.exec_prompt(prompt_text)

        def validator_fn(leader_res) -> bool:
            if not isinstance(leader_res, gl.vm.Return):
                return False
            a = self._score_of(leader_res.calldata)[0]
            b = self._score_of(leader_fn())[0]
            return abs(a - b) <= 10

        result = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
        score, reason = self._score_of(result)
        e.score = u256(score)
        e.status = u8(E_JUDGED)
        e.rationale = reason[:300]
        if int(c.has_winner) == 0 or score > int(c.best_score):
            c.best_score = u256(score)
            c.winner = e.author
            c.has_winner = u8(1)

    @gl.public.write
    def award(self, contest_id: int) -> None:
        c = self._get_contest(contest_id)
        if c.status != C_OPEN:
            raise gl.vm.UserError("contest already awarded")
        if int(c.has_winner) == 0:
            raise gl.vm.UserError("no judged entry to award")
        c.status = u8(C_CLOSED)
        self._pay(c.winner, c.prize)

    # ------------------------------------------------------------------ views
    @gl.public.view
    def get_contest_count(self) -> int:
        return len(self.contests)

    @gl.public.view
    def get_contest(self, contest_id: int) -> dict:
        c = self._get_contest(contest_id)
        return {
            "host": c.host.as_hex,
            "title": c.title,
            "prompt": c.prompt,
            "rubric": c.rubric,
            "prize": str(c.prize),
            "status": int(c.status),
            "winner": c.winner.as_hex,
            "best_score": int(c.best_score),
            "has_winner": int(c.has_winner),
        }

    @gl.public.view
    def get_entry_count(self) -> int:
        return len(self.entries)

    @gl.public.view
    def get_entry(self, entry_id: int) -> dict:
        e = self._get_entry(entry_id)
        return {
            "contest_id": int(e.contest_id),
            "author": e.author.as_hex,
            "title": e.title,
            "url": e.url,
            "score": int(e.score),
            "status": int(e.status),
            "rationale": e.rationale,
        }

    # -------------------------------------------------------------- internals
    def _get_contest(self, contest_id: int) -> Contest:
        if contest_id < 0 or contest_id >= len(self.contests):
            raise gl.vm.UserError("no such contest")
        return self.contests[contest_id]

    def _get_entry(self, entry_id: int) -> Entry:
        if entry_id < 0 or entry_id >= len(self.entries):
            raise gl.vm.UserError("no such entry")
        return self.entries[entry_id]

    def _score_of(self, result: typing.Any) -> tuple:
        data = result
        if isinstance(data, str):
            data = self._extract_json(data)
        if not isinstance(data, dict):
            return (0, "")
        raw = data.get("score", 0)
        reason = str(data.get("reason", ""))
        try:
            score = int(float(raw))
        except (ValueError, TypeError):
            score = 0
        if score < 0:
            score = 0
        if score > 100:
            score = 100
        return (score, reason)

    def _extract_json(self, text: str) -> typing.Any:
        try:
            return json.loads(text)
        except (ValueError, TypeError):
            pass
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except (ValueError, TypeError):
                return None
        return None

    def _pay(self, recipient: Address, amount: u256) -> None:
        if amount == u256(0):
            return
        _Payee(recipient).emit_transfer(value=amount)


@gl.evm.contract_interface
class _Payee:
    class View:
        pass

    class Write:
        pass
