# STATE.md — CTF Challenge Progress

## Pwn
### Very-Easy (19/19 complete)
| # | Challenge | Flag | Method |
|---|-----------|------|--------|
| 1 | Power-Greed | `HTB{p0w3R_g41d_r34ct1on}` | ret2win |
| 2 | Quack-Quack | `HTB{~c4n4ry_g035_qu4ck_qu4ck~}` | canary leak + ret2win |
| 3 | Blessing | `HTB{3v3ryth1ng_l00k5_345y_w1th_l34k5}` | heap leak, malloc fail → write-zero |
| 4 | El-Teteo | `HTB{3l_t3t30_d3_5h3llc0d3_0f_sk1d}` | ret2shellcode (NX disabled) |
| 5 | Mathematricks | `HTB{m4th3m4tINT_tr1ck_0R_tr34t}` | int32 overflow |
| 6 | El-Pipo | `HTB{3l_p1p0v3rfl0w_w1th_w3b}` | buffer overflow (web POST) |
| 7 | Entity | `HTB{th3_3nt1ty_0f_htb00_i5_5t1ll_h3r3}` | union type confusion |
| 8 | Getting-Started | `HTB{b0f_tut0r14l5_4r3_g00d}` | buffer overflow |
| 9 | Lesson | `HTB{w4rm35t_w4rmup_3v3r}` | Q&A trivia |
| 10 | Que-onda | `HTB{w3lc0m3_2_htb00_pwn_f35t1v4l}` | string compare ("flag") |
| 11 | Questionnaire | `HTB{l34rn_th3_b451c5_b3f0r4_u_5t4rt}` | Q&A (10 questions) |
| 12 | racecar | `HTB{02d259dbc9c68c662af079f9a9a502a1}` | format string, win race then leak flag |
| 13 | Regularity | `HTB{jMp_rSi_jUmP_aLl_tH3_w4y!}` | shellcode + jmp *%rsi |
| 14 | Sacred-Scrolls-Revenge | `HTB{s1gn3ed_sp3ll5_fr0m_th3_b01_wh0_l1v3d}` | uninit leak + ZIP upload + BOF ret2libc |
| 15 | Space-Pirate-Entry-Point | `HTB{g4t3_0n3_d4rkn3e55_th3_w0rld_0f_p1r4t35}` | format string %hn write |
| 16 | Space-Pirate-Going-Deeper | `HTB{d1g_1n51d3..u_Cry_cry_cry}` | 1-byte ret addr overwrite |
| 17 | Space-Pirate-Retribution | `HTB{w3_f1n4lly_m4d3_1t}` | uninit PIE leak + BOF + ret2libc |
| 18 | Vault-Breaker | `HTB{d4nz4_kudur0r0r0}` | strcpy null-byte key zeroing |
| 19 | Writing-on-the-Wall | `HTB{4n0th3r_br1ck_0n_th3_w4ll}` | off-by-one null byte, strcmp bypass |

### Easy
Not started.

### Medium
Not started.

### Hard
Not started.

## Crypto (8 challenges)
Not started.

## Forensics (10 challenges)
Not started.

## Web (29 challenges)
Not started.

## Malware / OSINT / Reverse / AI-ML / Misc
Not started.
