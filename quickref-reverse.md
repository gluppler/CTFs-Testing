# Reverse Engineering Quick Reference

```bash
# Static analysis
objdump -d binary | less
strings binary | grep -i flag
rabin2 -I binary  # file info
rabin2 -z binary  # strings

# Decompilation
ghidra  # GUI
r2 -A binary -c 'pdf @main'

# Dynamic
strace ./binary 2>&1 | tail -30
ltrace ./binary 2>&1 | tail -30
gdb -q binary -ex 'start' -ex 'disass main'

# APK
apktool d app.apk
jadx-gui app.apk

# WASM
wasm-decompile file.wasm

# .NET
ilspycmd binary.dll
```
