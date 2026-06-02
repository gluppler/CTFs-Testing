# Pwn Quick Reference

```bash
# Binary analysis
checksec --file=binary && file binary
objdump -d binary | grep '<main>:' -A100
strings -t x binary | grep -i 'flag\|win\|shell\|cat'
readelf -l binary | grep GNU_STACK  # check NX

# Pattern offset
python3 -c "from pwn import *; print(cyclic(200))"
python3 -c "from pwn import *; print(cyclic_find(0x61616164))"

# Run with bundled glibc
python3 -c "from pwn import *; p=process(['./glibc/ld-linux-x86-64.so.2','--library-path','./glibc/','./binary'],cwd='challenge'); p.interactive()"

# Find gadgets
ROPgadget --binary binary | grep -E 'pop rdi|ret'

# PDF text extraction
pdftotext challenge.pdf challenge.txt

# Shellcraft
python3 -c "from pwn import *; print(asm(shellcraft.sh()).hex())"

# One gadget
one_gadget libc.so.6

# GDB
gdb -q binary -ex 'start' -ex 'checksec'
```
