# Web

Content catalog for web exploitation challenges.

## Very Easy

### With writeups

- [Criticalops](Very-Easy/Criticalops/writeup.md) — Hardcoded JWT signing secret in client-side JavaScript allowed forging an admin JWT, revealing a support ticket with the flag.
- [JinjaCare](Very-Easy/JinjaCare/writeup.md) — SSTI via Jinja2 template injection in the profile name field rendered unsafely in a PDF certificate generator.
- [NeoVault](Very-Easy/NeoVault/writeup.md) — Next.js app with V1 API IDOR (download any user's transactions) and V2 NoSQL injection for user enumeration.
- [OpenSecret](Very-Easy/OpenSecret/writeup.md) — Hardcoded JWT secret in client JS allowed forging an admin session to read protected tickets.
- [OnlyHacks](Very-Easy/OnlyHacks/writeup.md) — IDOR in the chat room `rid` parameter allowed accessing another user's chat history containing the flag.
- [WayWitch](Very-Easy/WayWitch/writeup.md) — Hardcoded JWT signing secret (`halloween-secret`) in server-side source code allowed forging an admin JWT to read tickets containing the flag.
- [Void-Whispers](Very-Easy/Void-Whispers/writeup.md) — Command injection via `shell_exec("which $sendMailPath")` with `${IFS}` whitespace bypass to copy flag to web root.

### Pending

- Armaxis
- CandyVault
- Cursed-Secret-Party
- Gunship
- Juggling-facts
- KORP-Terminal
- Phantom-Script
- SpookTastic
- TimeKORP
- Trapped-Source
- Unholy-Union

## Easy

- Blackout-Ops
- CitiSmart
- NexusSeven
- NovaEnergy
- Offlinea
- Secure-Notes
- SpeedNet
- Volnaya-Forums

## Medium

- [Notebook-Converter-Pro](Medium/Notebook-Converter-Pro/writeup.md) — nbconvert LFI via `embed_images=True` extracts SQLite DB with plaintext admin password; attachment name path traversal overwrites converter code for RCE via `/readflag`.

## Hard

*(No challenges yet.)*

## Insane

*(No challenges yet.)*
