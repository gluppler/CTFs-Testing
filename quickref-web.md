# Web Quick Reference

```bash
# Fuzzing
ffuf -u https://<target>/FUZZ -w wordlist.txt -fc 403
feroxbuster -u https://<target> -w wordlist.txt
wfuzz -c -z file,wordlist.txt https://<target>/FUZZ

# Curl shortcuts
curl -sk https://<target>/ | head -50
curl -skL http://<target>:<port>/ 
curl -sk -X POST https://<target>/api -H 'Content-Type: application/json' -d '{"key":"value"}'

# SQLi quick test
sqlmap -u "https://<target>/page?id=1" --batch

# SSTI test
curl -sk 'https://<target>/{{7*7}}'

# JWT decode
python3 -c "import jwt; print(jwt.decode(token, options={'verify_signature':False}))"
```
