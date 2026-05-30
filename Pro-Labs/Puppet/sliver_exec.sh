#!/bin/bash
# Usage: ./sliver_exec.sh <beacon_id> <command>
SESSION="sliver_exec"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SLIVER_BIN="$SCRIPT_DIR/sliver-client_linux"
OUTFILE="/tmp/sliver_out.txt"

tmux kill-session -t "$SESSION" 2>/dev/null
sleep 0.3
tmux new-session -d -s "$SESSION" "$SLIVER_BIN console" 2>/dev/null
sleep 8
tmux send-keys -t "$SESSION" Enter
sleep 2

TARGET="$1"
CMD="$2"
WAIT="${3:-15}"

if [ -n "$TARGET" ]; then
    tmux send-keys -t "$SESSION" "use $TARGET" Enter
    sleep 2
fi
if [ -n "$CMD" ]; then
    tmux send-keys -t "$SESSION" "$CMD" Enter
    sleep "$WAIT"
fi

tmux capture-pane -t "$SESSION" -p -S -32768 > "$OUTFILE"
tmux send-keys -t "$SESSION" "exit" Enter
sleep 1
tmux kill-session -t "$SESSION" 2>/dev/null
perl -pe 's/\e\[[0-9;]*[a-zA-Z]//g; s/\e\][0-9;]*[^\a]*\a//g; s/\r\n/\n/g' "$OUTFILE"
