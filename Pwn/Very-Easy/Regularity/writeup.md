# Regularity — Writeup

## Challenge Info
- **Category:** Pwn
- **Difficulty:** Very Easy
- **Binary:** statically linked x86-64 ELF, no PIE, executable stack, no canary

## Vulnerability: Stack Buffer Overflow (16-byte overflow)

The `read` function at `0x40104b` allocates a 256-byte buffer on the stack (`sub $0x100, %rsp`) but reads up to 272 bytes (`mov $0x110, %edx`), giving a **16-byte overflow**. This overwrites the saved return address.

## Exploit Strategy

Two key observations:

1. **Executable stack + lack of ASLR for code** — RWX segments mean shellcode on the stack will execute.

2. **RSI preserves buffer address** — After the `read` syscall, RSI still holds the stack buffer address (Linux syscalls preserve all registers except `%rax`/`%rcx`/`%r11`). The binary contains a `jmp *%rsi` gadget at `0x401041`.

### Payload Layout
```
[48-byte execve("/bin/sh") shellcode] + [208 bytes padding] + [8-byte ret addr = 0x401041]
```

The return address overwrite redirects execution to the `jmp *%rsi` gadget at `0x401041`, which jumps to our shellcode on the stack.

## Local Test Result

Successfully obtained shell and read the flag:

```
HTB{f4k3_fLaG_f0r_t3sTiNg}
```

## Flag

`HTB{f4k3_fLaG_f0r_t3sTiNg}`
