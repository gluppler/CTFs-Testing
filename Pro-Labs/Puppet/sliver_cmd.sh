#!/bin/bash
SESSION="sliver_puppet"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SLIVER_BIN="$SCRIPT_DIR/sliver-client_linux"
OUTFILE="/tmp/sliver_out.txt"
TARGET="$1"
CMD1="$2"
CMD2="$3"

tmux kill-session -t "$SESSION" 2>/dev/null
sleep 0.3
tmux new-session -d -s "$SESSION" "$SLIVER_BIN console"
sleep 4
tmux send-keys -t "$SESSION" Enter
sleep 2

if [ -n "$TARGET" ]; then
    tmux send-keys -t "$SESSION" "use $TARGET" Enter
    sleep 1
fi

if [ -n "$CMD1" ]; then
    tmux send-keys -t "$SESSION" "$CMD1" Enter
    sleep 3
fi

if [ -n "$CMD2" ]; then
    tmux send-keys -t "$SESSION" "$CMD2" Enter
    sleep 15
fi

tmux capture-pane -t "$SESSION" -p -S - > "$OUTFILE"
tmux send-keys -t "$SESSION" "exit" Enter
sleep 1
tmux kill-session -t "$SESSION" 2>/dev/null

cat "$OUTFILE" | perl -pe 's/\e\[[0-9;]*[a-zA-Z]//g; s/\e\][0-9;]*[^\a]*\a//g; s/\r//g'
