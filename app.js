import { makeReader, write, connectWallet, activeAccount, balanceOf, short, toGen, GEN, fmtErr }
  from "./shared/genlayer-lite.js";
import { mountReviewDesk } from "./shared/review-desk.js";

const CONTRACT = "0x065566Ea5d90d3f485956a7dF2Cf6F1BD8Dd6a3A";
const { read } = makeReader(CONTRACT);
const C_OPEN = 0, C_CLOSED = 1, E_PENDING = 0, E_JUDGED = 1;
let account = null, contests = [], entries = [];
const $ = (id) => document.getElementById(id);

queueMicrotask(() => mountReviewDesk({
  contract: CONTRACT, read, write, ensureWallet, fmtErr,
  entity: "Contest ruling", idLabel: "Contest ID", countMethod: "get_claim_count", recordMethod: "get_claim_record",
  openWindowMethod: "open_challenge_window", submitChallengeMethod: "submit_challenge", resolveChallengeMethod: "resolve_challenge_with_genlayer",
  submitAppealMethod: "submit_appeal", resolveAppealMethod: "resolve_appeal_with_genlayer", archiveMethod: "archive_claim",
  variant: "ribbon", kicker: "Rubric review", title: "Quill judging bench",
  intro: "Inspect the recorded contest ruling, challenge a scoring error with the source entry, and settle the appeal before the result is archived.",
}));
const esc = (s) => (s || "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const isZero = (a) => !a || /^0x0+$/.test(a);

$("contractLink").textContent = "Contract " + short(CONTRACT);

function toast(msg, kind = "", title = "quill") {
  const el = document.createElement("div"); el.className = "toast " + kind;
  el.innerHTML = `<span class="tt">${title}</span>`; el.appendChild(document.createTextNode(msg));
  $("log").appendChild(el); setTimeout(() => el.remove(), kind === "err" ? 15000 : 5000);
}

async function refreshWallet() {
  account = await activeAccount();
  const slot = $("walletslot");
  if (account) { let bal = 0n; try { bal = await balanceOf(account); } catch (_) {} slot.innerHTML = `<span class="mono" style="font-size:12.5px;color:var(--mut)">${short(account)} \u00b7 ${toGen(bal)} GEN</span>`; }
  else { slot.innerHTML = `<button class="btn ghost sm" id="connectBtn">Connect</button>`; $("connectBtn").onclick = doConnect; }
}
async function doConnect() { try { account = await connectWallet(); toast("Connected on studionet.", "ok"); await refreshWallet(); } catch (e) { toast(fmtErr(e), "err"); } }
async function ensureWallet() { if (!account) account = await connectWallet(); await refreshWallet(); }

const entriesFor = (cid) => entries.filter((e) => Number(e.contest_id) === cid);

async function load() {
  try {
    const [ccRaw, ecRaw] = await Promise.all([read("get_contest_count"), read("get_entry_count")]);
    const cc = Number(ccRaw), ec = Number(ecRaw);
    const [cs, es] = await Promise.all([
      Promise.all(Array.from({ length: cc }, (_, i) => read("get_contest", [i]).then((record) => ({ id: i, ...record })))),
      Promise.all(Array.from({ length: ec }, (_, i) => read("get_entry", [i]).then((record) => ({ id: i, ...record })))),
    ]);
    contests = cs; entries = es; renderList();
    $("stContests").textContent = cc;
    $("stPrize").textContent = toGen(cs.reduce((a, c) => a + BigInt(c.prize), 0n).toString());
    $("stEntries").textContent = ec;
  } catch (e) { $("contestList").innerHTML = `<div class="c-empty">Could not reach the chain. ${fmtErr(e)}</div>`; }
}

function renderList() {
  const el = $("contestList");
  if (!contests.length) { el.innerHTML = `<div class="c-empty">No contests yet. Open the first one.</div>`; return; }
  el.innerHTML = "";
  [...contests].reverse().forEach((c) => {
    const st = Number(c.status);
    const es = entriesFor(c.id).slice().sort((a, b) => {
      const aj = Number(a.status) === E_JUDGED, bj = Number(b.status) === E_JUDGED;
      if (aj && bj) return Number(b.score) - Number(a.score);
      return aj ? -1 : bj ? 1 : 0;
    });
    const wrap = document.createElement("div"); wrap.className = "contest";
    const rows = es.length ? es.map((e, i) => {
      const ej = Number(e.status) === E_JUDGED;
      const isWin = st !== C_OPEN || Number(c.has_winner) === 1 ? (!isZero(c.winner) && e.author.toLowerCase() === c.winner.toLowerCase() && ej) : false;
      const judgeBtn = (st === C_OPEN && !ej) ? `<button class="btn sm judgeBtn" data-eid="${e.id}">Judge</button>` : "";
      const score = ej ? `<span class="score">${e.score}<small>/100</small></span>` : `<span class="score pending">Unjudged</span>`;
      return `<div class="entry ${isWin ? "win" : ""}">
          <div class="entry-rank">${ej ? (i + 1) : "\u2014"}</div>
          <div class="entry-m"><div class="entry-title">${isWin ? '<span class="crown">\u265B</span>' : ""}${esc(e.title)}</div><div class="entry-by">by ${short(e.author)} \u00b7 <a href="${esc(e.url)}" target="_blank" rel="noopener">read \u2197</a></div></div>
          <div class="entry-r">${score}${judgeBtn}</div>
          ${ej && e.rationale ? `<div class="entry-reason">"${esc(e.rationale)}"</div>` : ""}
        </div>`;
    }).join("") : `<div class="entry"><div class="entry-rank">\u2014</div><div class="entry-m"><div class="entry-by">No entries yet.</div></div><div></div></div>`;
    let actions = "";
    if (st === C_OPEN) {
      actions = `<button class="btn gold submitBtn" data-cid="${c.id}">Submit an entry</button>`;
      if (Number(c.has_winner) === 1) actions += `<button class="btn awardBtn" data-cid="${c.id}">Award the prize \u2192</button>`;
    } else {
      actions = `<span style="font-family:var(--mono);font-size:12px;color:var(--mut)">PRIZE AWARDED \u00b7 WINNER ${short(c.winner)} \u00b7 SCORE ${c.best_score}/100</span>`;
    }
    wrap.innerHTML = `
      <div class="contest-h">
        <div class="contest-top"><h2 class="contest-title">${esc(c.title)}</h2><span class="cbadge ${st === C_OPEN ? "cb-open" : "cb-closed"}">${st === C_OPEN ? "Open" : "Awarded"}</span></div>
        <p class="contest-prompt">${esc(c.prompt)}</p>
        <div class="contest-meta"><span>PRIZE <b>${toGen(c.prize)} GEN</b></span><span>RUBRIC ${esc(c.rubric)}</span></div>
      </div>
      <div class="board"><div class="board-t">Entries \u00b7 ranked by score</div>${rows}</div>
      <div class="contest-actions">${actions}</div>`;
    el.appendChild(wrap);
  });
  document.querySelectorAll(".judgeBtn").forEach((b) => b.onclick = () => doJudge(Number(b.dataset.eid)));
  document.querySelectorAll(".submitBtn").forEach((b) => b.onclick = () => openSubmit(Number(b.dataset.cid)));
  document.querySelectorAll(".awardBtn").forEach((b) => b.onclick = () => doAward(Number(b.dataset.cid)));
}

function openDrawer() { $("scrim").classList.add("on"); $("drawer").classList.add("on"); }
function closeDrawer() { $("scrim").classList.remove("on"); $("drawer").classList.remove("on"); }

function openNew() {
  $("drawerTitle").textContent = "A call for entries";
  $("drawerBody").innerHTML = `
    <p>Post a prompt, set the rubric writers are judged against, and fund the prize.</p>
    <label>Contest title</label><input id="nCTitle" maxlength="90" placeholder="The Consensus Essay Prize" autocomplete="off" />
    <label>Prompt</label><textarea id="nPrompt" placeholder="What should writers respond to?"></textarea>
    <label>Judging rubric</label><textarea id="nRubric" placeholder="What makes a winning entry? Clarity, originality, argument..."></textarea>
    <label>Prize pool (GEN)</label><input id="nPrize" type="number" min="0" step="0.5" value="10" style="font-family:var(--mono)" />
    <button class="btn gold block" id="createBtn">Fund prize & open contest</button>`;
  $("createBtn").onclick = doCreate; openDrawer();
}

function openSubmit(cid) {
  const c = contests.find((x) => x.id === cid); if (!c) return;
  $("drawerTitle").textContent = "Submit a manuscript";
  $("drawerBody").innerHTML = `
    <p>Entering "${esc(c.title)}" \u2014 prize ${toGen(c.prize)} GEN.</p>
    <input id="nETitle" class="ms-title" maxlength="100" placeholder="Title of your piece" autocomplete="off" />
    <label>Public URL of the work</label><input id="nEUrl" placeholder="https://... where the judges can read it" autocomplete="off" />
    <p class="hint">VALIDATORS WILL READ IT AGAINST THE RUBRIC AND SCORE IT 0\u2013100.</p>
    <button class="btn gold block" id="submitBtn2">Submit entry</button>`;
  $("submitBtn2").onclick = () => doSubmit(cid); openDrawer();
}

async function doCreate() {
  const title = $("nCTitle").value.trim(), prompt = $("nPrompt").value.trim(), rubric = $("nRubric").value.trim(), prize = parseFloat($("nPrize").value);
  if (!title) return toast("Give the contest a title.", "err");
  if (!prompt) return toast("Write the prompt.", "err");
  if (!rubric) return toast("Set the rubric.", "err");
  if (!(prize > 0)) return toast("Fund a prize above zero.", "err");
  const btn = $("createBtn"); btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> opening';
  try { await ensureWallet(); await write(CONTRACT, "open_contest", [title, prompt, rubric], GEN(prize)); toast("Contest opened.", "ok"); closeDrawer(); await load(); }
  catch (e) { toast(fmtErr(e), "err"); btn.disabled = false; btn.innerHTML = "Fund prize & open contest"; }
}
async function doSubmit(cid) {
  const title = $("nETitle").value.trim(), url = $("nEUrl").value.trim();
  if (!title) return toast("Title your entry.", "err");
  if (!url) return toast("Add the public URL.", "err");
  const btn = $("submitBtn2"); btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> submitting';
  try { await ensureWallet(); await write(CONTRACT, "submit_entry", [cid, title, url]); toast("Entry submitted.", "ok"); closeDrawer(); await load(); }
  catch (e) { toast(fmtErr(e), "err"); btn.disabled = false; btn.textContent = "Submit entry"; }
}
async function doJudge(eid) {
  if (!confirm("Judge this entry? Validators read it against the rubric and score it 0-100. Calls a real LLM.")) return;
  toast("Validators reading the entry\u2026", "", "judge");
  try { await ensureWallet(); await write(CONTRACT, "judge_entry", [eid]); toast("Scored on-chain.", "ok"); await load(); }
  catch (e) { toast(fmtErr(e), "err"); }
}
async function doAward(cid) {
  if (!confirm("Award the prize to the current top-scored entry? This closes the contest.")) return;
  try { await ensureWallet(); await write(CONTRACT, "award", [cid]); toast("Prize awarded.", "ok"); await load(); }
  catch (e) { toast(fmtErr(e), "err"); }
}

$("navPostBtn").onclick = openNew;
$("refreshBtn").onclick = load;
$("closeDrawer").onclick = closeDrawer;
$("scrim").onclick = closeDrawer;
const _cb = $("connectBtn"); if (_cb) _cb.onclick = doConnect;
if (window.ethereum) window.ethereum.on?.("accountsChanged", refreshWallet);

refreshWallet();
load();
