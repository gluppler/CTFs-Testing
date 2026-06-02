# Lesson — Very-Easy Pwn Writeup

## Challenge

A trivial Q&A challenge teaching basic C/binary analysis. The provided binary has a buffer overflow (`scanf("%s")` into a 32-byte buffer), but exploitation is not required. Instead, connect to the remote service and answer 8 questions about the binary.

## Analysis

**Binary protections** (`checksec`):
- No PIE — fixed addresses
- No Canary — stack overflow possible
- NX enabled — no shellcode on stack
- Full RELRO — GOT read-only

**Vulnerability**: In `main()`, `scanf("%s", name)` reads unbounded input into a 32-byte stack buffer `name[0x20]`. This allows overwriting saved RBP and return address past byte 40.

**Overflow confirmation**:
- 39 bytes → clean exit
- 40 bytes → SIGSEGV (RIP overwrite at offset 40)

## Exploit

Two modes:
1. **Local**: 40 bytes padding + return address → demonstrates RIP control (crashes or redirects to `under_construction()`)
2. **Remote**: Automates the 8 Q&A questions:
   | Q | Answer |
   |---|--------|
   | 1 (32 or 64 bit?) | `64-bit` |
   | 2 (Which protection?) | `NX` |
   | 3 (Enter "Welcome admin!") | `Admin` |
   | 4 (name buffer size?) | `0x20` |
   | 5 (Never-called function?) | `under_construction` |
   | 6 (BOF-triggering function?) | `scanf` |
   | 7 (Bytes to segfault?) | `40` |
   | 8 (Address of `under_construction`?) | `0x4011d6` |

## Flag

Only available from the remote challenge service after answering all 8 questions correctly.
