#!/bin/bash
SESSION="sliver_interactive"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SLIVER_BIN="$SCRIPT_DIR/sliver-client_linux"
OUTFILE="/tmp/sliver_out.txt"

if ! tmux has-session -t "$SESSION" 2>/dev/null; then
    tmux new-session -d -s "$SESSION" -x 200 -y 50 "$SLIVER_BIN console"
    sleep 6
    tmux send-keys -t "$SESSION" Enter
    sleep 3
fi

CMD="$1"
[ -n "$CMD" ] && tmux send-keys -t "$SESSION" "$CMD" Enter
sleep 4
tmux capture-pane -t "$SESSION" -p -S -200 > "$OUTFILE"
perl -pe 's/\e\[[0-9;]*[a-zA-Z]//g; s/\e\][0-9;]*[^\a]*\a//g; s/\r//g' "$OUTFILE"
