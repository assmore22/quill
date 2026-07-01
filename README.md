# Quill V2

A GenLayer writing-prize court.

This repo packages the public casework UI and the GenLayer contract behind it: filings, evidence, review windows, challenge paths and final resolution.

## Quill Brief

Quill V2 (# v0.2.16), 65947 bytes, 40 write + 28 view.

The important files are:

- `contracts/quill_v2.py` - GenLayer contract source
- `deployment.json` - Studionet address, deploy transaction and smoke transaction hashes
- `index.html` and `app.js` - static frontend
- `README.md` - this operator and reviewer guide

## Quill On Studionet

- Network: studionet (61999)
- Contract: [0x065566Ea5d90d3f485956a7dF2Cf6F1BD8Dd6a3A](https://explorer-studio.genlayer.com/contracts/0x065566Ea5d90d3f485956a7dF2Cf6F1BD8Dd6a3A)
- Deploy tx: [0x38bd4127...3dc662](https://explorer-studio.genlayer.com/tx/0x38bd4127adc4e38cb0f5b9ca65489541223a926cfbeb2f911b0822b72e3dc662)
- Deployed at: 2026-06-24T01:55:50.488Z
- Smoke writes recorded: 20

## Adjudication Mechanics

Typical flow: `open_claim` -> `submit_entry` -> `review_dispute_with_genlayer` -> `resolve` -> `challenge` -> `submit_appeal` -> `set_claim_standard` -> `archive_dispute`

Useful reads: `get_claim_count`, `get_dispute_count`, `get_contest_count`, `get_entry_count`, `get_claim`, `get_dispute`, `get_contest`, `get_entry`

- Primary source: `contracts/quill_v2.py` (65,947 bytes)
- Public write/action methods: 40
- Read methods: 28
- GenLayer features: live web rendering, LLM adjudication, validator-comparative consensus, indexed storage, append-only collections

## Smoke Trail

- set_claim_standard: [0x1985b695...392a51](https://explorer-studio.genlayer.com/tx/0x1985b6957eb418431e6fd156e65d1620c202f03a8dd40cc198239fcd31392a51)
- open_contest: [0x0107d373...59c5af](https://explorer-studio.genlayer.com/tx/0x0107d37329faffa2b023ded768bfb2b8c9c8e0f04ec6d603c5d4dc5a0b59c5af)
- submit_entry: [0x1171225f...efac54](https://explorer-studio.genlayer.com/tx/0x1171225fdd6be1813f31e775e198f533f9deaff9df34c6e7fca367abebefac54)
- add_obligation: [0x6f442f79...0661bd](https://explorer-studio.genlayer.com/tx/0x6f442f790dab2e56b867b187715f765c962cc54f523b3633885eddb4170661bd)
- add_evidence_docs: [0x11a6e6bf...f0487d](https://explorer-studio.genlayer.com/tx/0x11a6e6bf1ae65b1d3c6639ee145f19516e155801627a49232b1f37fd20f0487d)
- add_evidence_web: [0x2a0e961a...15f5b4](https://explorer-studio.genlayer.com/tx/0x2a0e961aff1498fc50212c7860ed5400ec9f32f994a0e679fc8b9f8a5115f5b4)
- judge_entry: [0x61134a3a...375f54](https://explorer-studio.genlayer.com/tx/0x61134a3aed54f393e4b539086020d9afdfc4436fea9414bf4bb2173995375f54)
- open_review: [0x59552aa1...14876c](https://explorer-studio.genlayer.com/tx/0x59552aa1d2d9d32afb7e76f9cb34da1eeec936e82e8376d4c2e6f84d6514876c)

## Run Quill Locally

```powershell
cd <private-workspace-root>
npm run preview:start
npm run preview:project -- 21-quill
```

Open http://localhost:8080/21-quill/.

## Publish Quill

```powershell
cd <private-workspace-root>
npm run publish:project -- -Project 21-quill -Repo https://github.com/aspro45/<repo-name>.git
```

## Keys And Boundaries

- This repository should contain no decrypted wallet material.
- The Studionet deployer private key stays in the local encrypted vault.
- Vercel deployment should use the project folder only.

- QA notes: Upgraded from a compact writing contest MVP into Quill V2. Smoke: set_claim_standard / open_contest / submit_entry / add_obligation / two add_evidence calls / judge_entry / open_review / review_claim_with_genlayer / open_challenge_window / submit_challenge...
