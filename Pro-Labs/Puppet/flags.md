# Puppet — Captured Flags

| # | Flag | Location | Method |
|---|------|----------|--------|
| 1 | `PUppET{1c1740d66f707111a911e5f6a96d7d36}` | FILE01: `C:\Users\bruce.smith\Desktop\flag.txt` | Initial beacon access via Sliver C2 |
| 2 | `PUPPET\root` user password | DC01: DPAPI blob in `C:\Windows\System32\config\systemprofile\AppData\Local\Microsoft\Credentials\` | Puppet manifest exec → svc_puppet_win_t0 → `sharpdpapi machinetriage` |

## Flag Locations Summary
- **Flag #1**: File on Bruce.Smith's desktop (first beacon access)
- **Flag #2**: `root.txt` at `C:\Users\Administrator\Desktop\root.txt` says *"The final flag is the password of the user 'PUPPET\root'"*. Extract via SharpDPAPI: `sharpdpapi machinetriage` → look for `TargetName: Domain:batch=TaskScheduler:Task:{...}` with `UserName: PUPPET\root` → `Credential` field is the flag.
