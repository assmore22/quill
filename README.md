# Quill

Writing contests judged against public rubrics and evidence.

Quill turns creative submissions into auditable contest entries. Entries, judging criteria, supporting sources and review results all stay readable on-chain.

## Review Links

| Surface | Link |
| --- | --- |
| Live app | https://assmore22-quill.vercel.app |
| GitHub | https://github.com/assmore22/quill |
| Contract | https://explorer-studio.genlayer.com/address/0x065566Ea5d90d3f485956a7dF2Cf6F1BD8Dd6a3A |

## Chain Record

- Network: GenLayer Studionet
- Chain ID: 61999
- Contract: `0x065566Ea5d90d3f485956a7dF2Cf6F1BD8Dd6a3A`
- Deploy transaction: [0x38bd4127...3dc662](https://explorer-studio.genlayer.com/tx/0x38bd4127adc4e38cb0f5b9ca65489541223a926cfbeb2f911b0822b72e3dc662)
- Deployed: `2026-06-24T01:55:50.488Z`
- Source: `contracts/quill_v2.py` (65,947 bytes)

## Protocol Path

1. Open a contest.
2. Submit an entry.
3. Attach rubric evidence.
4. Judge with GenLayer.
5. Handle challenge and appeal paths.

The frontend reads contest records, entry lists, scorecards and challenge history. Contract state is public; write actions still require a connected wallet on GenLayer Studionet.

## Finalized Smoke

| Action | Transaction |
| --- | --- |
| `set_claim_standard` | [0x1985b695...392a51](https://explorer-studio.genlayer.com/tx/0x1985b6957eb418431e6fd156e65d1620c202f03a8dd40cc198239fcd31392a51) |
| `open_contest` | [0x0107d373...59c5af](https://explorer-studio.genlayer.com/tx/0x0107d37329faffa2b023ded768bfb2b8c9c8e0f04ec6d603c5d4dc5a0b59c5af) |
| `submit_entry` | [0x1171225f...efac54](https://explorer-studio.genlayer.com/tx/0x1171225fdd6be1813f31e775e198f533f9deaff9df34c6e7fca367abebefac54) |
| `add_obligation` | [0x6f442f79...0661bd](https://explorer-studio.genlayer.com/tx/0x6f442f790dab2e56b867b187715f765c962cc54f523b3633885eddb4170661bd) |
| `add_evidence_docs` | [0x11a6e6bf...f0487d](https://explorer-studio.genlayer.com/tx/0x11a6e6bf1ae65b1d3c6639ee145f19516e155801627a49232b1f37fd20f0487d) |
| `add_evidence_web` | [0x2a0e961a...15f5b4](https://explorer-studio.genlayer.com/tx/0x2a0e961aff1498fc50212c7860ed5400ec9f32f994a0e679fc8b9f8a5115f5b4) |

## Local Run

```bash
python -m http.server 8080
```

Open `http://localhost:8080`.

## Release Hygiene

The public package is static and has no install step. Vercel receives only frontend, contract source and public deployment metadata.

Keep wallet private keys, vault exports, `.env` files, Vercel project state and dashboard data out of Git. This repository is for public source, UI, tests and deployment receipts only.
