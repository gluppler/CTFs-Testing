# Web Action Log

## 2026-05-26

- **Notebook-Converter-Pro** — Solved Flask + nbconvert challenge. Chain: LFI via nbconvert markdown image embedding (`embed_images=True`) to download SQLite DB → extract admin plaintext password → admin login → enable asset storage → overwrite converter via attachment name path traversal (`../../../../app/converter/convert_job.py`) → trigger conversion runs `/readflag`. Flag: `HTB{y3t_4n0th3r_pyth0n_c0nv3rt3r_cve}`
- **SpeedNet** — Unsolved. GraphQL ISP challenge with devForgotPassword (leaks reset tokens), admin 2FA that cannot be bypassed. Reset admin's password via devForgotPassword but blocked by 2FA OTP sent to admin@speednet.htb (inaccessible). Brute forced 0-99999 OTPs with no match. NoSQLi, JWT manipulation, IDOR, mass assignment all blocked. Public writeups confirm brute-force approach (range 1000-999999) but it failed on this instance.
- **Void-Whispers** — Solved command injection challenge. `sendMailPath` passes through `shell_exec("which $sendMailPath")` with only a space filter. Used `${IFS}` to bypass and `cp` the flag to web root. Flag: `HTB{c0mm4nd_1nj3ct1on_15_3457_t0_f1nD!}`
- **WayWitch** — Solved hardcoded JWT secret challenge. `halloween-secret` found in `util.js`, forged admin JWT, accessed `/tickets` to read admin ticket containing the flag. Flag: `HTB{k33p_th3s3_jwt_s3cr3t_s4f3f_br0}`
- **Web Automation** — Created `Web/scripts/` with `pipeline.sh`, `jwt-forge.sh`, `ssti-exploit.sh`, `idor-enum.sh`, `nosqli-enum.sh`, `web-recon.sh`.

## 2026-05-23

- **OnlyHacks** — Solved IDOR challenge. `/chat/?rid=3` renders a seeded user's chat room with the flag; no auth check on the `rid` parameter. Flag: `HTB{d0nt_trust_str4ng3r5_bl1ndly}`

## 2026-05-22

- **Criticalops** — Solved hardcoded JWT secret challenge. Extracted `SecretKey-CriticalOps-2025` from client JS, forged admin JWT, read `/api/tickets`. Flag: `HTB{Wh0_Put_JWT_1n_Cl13nt_S1d3_lm4o}`
- **OpenSecret** — Solved hardcoded JWT secret challenge. Extracted `HTB{0p3n_s3cr3ts_ar3_n0t_s3cr3ts}` from inline script, forged admin session cookie, read `/tickets`. Flag: `HTB{0p3n_s3cr3ts_ar3_n0t_s3cr3ts}`
- **JinjaCare** — Solved SSTI challenge. Injected `{{lipsum.__globals__['os'].popen('cat /flag.txt').read()}}` into profile name, rendered in PDF. Flag: `HTB{v3ry_e4sy_sst1_r1ght?}`
- **NeoVault** — Solved IDOR + NoSQLi challenge. Used V2 `inquire` endpoint with `$ne` injection to enumerate users, then V1 `download-transactions` IDOR to get `user_with_flag`'s statement PDF. Flag: `HTB{n0t_s0_3asy_1d0r}`
