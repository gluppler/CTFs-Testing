#!/bin/bash
SESSION="sliver"
OUTFILE="/tmp/beacon_cmd.txt"

CMD="$1"
WAIT="${2:-90}"

tmux send-keys -t "$SESSION" "$CMD" Enter
echo "[*] Tasked: $CMD"
echo "[*] Waiting ${WAIT}s for beacon check-in..."
sleep "$WAIT"

tmux capture-pane -t "$SESSION" -p -S - | perl -pe 's/\e\[[0-9;]*[a-zA-Z]//g; s/\e\][0-9;]*[^\a]*\a//g; s/\r//g' > "$OUTFILE"

echo "=== OUTPUT ==="
grep -A9999 "\[*\] Tasked beacon\|\[*\] completed task\|\[+\] .* completed\|\[-\] .* failed" "$OUTFILE" | tail -50
echo "=== END ==="
echo "[*] Full output in $OUTFILE"
